import threading
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import RobustScaler, StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any

SUPPORTED_MODELS = ('isolation_forest', 'lof', 'ocsvm', 'autoencoder')

# Autoenkoder uczy się na danych przyciętych do ±AE_TRAIN_CLIP (po skalowaniu odpornym na wartości skrajne).
# Bez tego sieć uczy się odtwarzać także skrajne punkty, przez co anomalie dostają niski błąd rekonstrukcji.
# Dobrane eksperymentalnie (6 spółek x 5 przebiegów): F1 0.50 -> 0.76 (batch), 0.51 -> 0.55 (walk-forward).
AE_TRAIN_CLIP = 5.0

# Inicjalizacja wag autoenkodera korzysta z globalnego RNG torcha – blokada zapewnia
# powtarzalne wyniki, gdy detekcja działa równolegle w wielu wątkach (benchmark)
_TORCH_INIT_LOCK = threading.Lock()

# Tryby detekcji:
# - 'batch': model uczony i oceniany na całym okresie (analiza historyczna, "widzi" przyszłość)
# - 'walk_forward': każda sesja oceniana modelem uczonym wyłącznie na sesjach wcześniejszych
SUPPORTED_MODES = ('batch', 'walk_forward')
# Walk-forward: minimalna liczba sesji treningowych i co ile sesji model jest douczany
WALK_FORWARD_MIN_TRAIN = 60
WALK_FORWARD_REFIT_EVERY = 10
# Część okna treningowego (najnowsze sesje) odkładana do kalibracji progu anomalii
WALK_FORWARD_CALIBRATION_SHARE = 0.3
WALK_FORWARD_MIN_CALIBRATION = 20

# Sygnały starsze niż tyle dni od ostatniej sesji są wygaszane do 'Hold'
SIGNAL_LOOKBACK_DAYS = 60

FEATURES = [
    'returns', 'volatility', 'rsi', 'atr',
    'return_1d', 'return_3d', 'return_7d',
    'volume_change', 'volume_ratio',
    'dist_to_ema20', 'bb_position', 'z_score_20', 'volatility_change',
    'momentum_5d', 'drawdown', 'body', 'upper_shadow', 'lower_shadow'
]


class TabularAutoencoder(nn.Module):
    def __init__(self, input_dim: int):
        super(TabularAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, max(input_dim // 2, 4)),
            nn.ReLU(),
            nn.Linear(max(input_dim // 2, 4), max(input_dim // 4, 2)),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(max(input_dim // 4, 2), max(input_dim // 2, 4)),
            nn.ReLU(),
            nn.Linear(max(input_dim // 2, 4), input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


class AnomalyDetector:
    @staticmethod
    def build_features(df: pd.DataFrame, impute: bool = True) -> pd.DataFrame:
        """
        Buduje macierz cech dla modeli. Wszystkie cechy są względne (niezależne od skali ceny/wolumenu)
        i przyczynowe – wartość dla sesji t zależy wyłącznie od sesji <= t.
        Braki z okresu rozgrzewki wskaźników (pierwsze ~20 sesji) uzupełniane są medianą cechy,
        aby nie tworzyć sztucznych wartości skrajnych (np. RSI = 0), które modele uznałyby za anomalie.
        Przy impute=False braki zostają (walk-forward uzupełnia je medianą z okna treningowego).
        """
        close = df['close']
        candle_scale = close.replace(0, np.nan)

        feats = pd.DataFrame(index=df.index)
        feats['returns'] = df['returns']
        feats['volatility'] = df['volatility'] / candle_scale
        feats['rsi'] = df['rsi']
        feats['atr'] = df['atr'] / candle_scale

        # Stopy zwrotu w różnych horyzontach
        feats['return_1d'] = close.pct_change(1)
        feats['return_3d'] = close.pct_change(3)
        feats['return_7d'] = close.pct_change(7)

        # Wolumen względem własnej średniej
        feats['volume_change'] = df['volume'].pct_change(1)
        feats['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean().replace(0, np.nan)

        # Cechy odległościowe i pozycyjne (bezpieczne przed dzieleniem przez 0)
        feats['dist_to_ema20'] = (close - df['ema_20']) / df['ema_20'].replace(0, np.nan)
        bb_width = (df['bb_upper'] - df['bb_lower']).replace(0, np.nan)
        feats['bb_position'] = (close - df['bb_lower']) / bb_width
        rolling_std_20 = close.rolling(window=20).std().replace(0, np.nan)
        feats['z_score_20'] = (close - df['sma_20']) / rolling_std_20
        feats['volatility_change'] = df['volatility'].pct_change(1)

        # Momentum, drawdown i struktura świec (znormalizowane ceną)
        feats['momentum_5d'] = close.pct_change(5)
        rolling_max = close.cummax()
        feats['drawdown'] = (close - rolling_max) / rolling_max.replace(0, np.nan)
        feats['body'] = (close - df['open']).abs() / candle_scale
        feats['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / candle_scale
        feats['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / candle_scale

        feats = feats.replace([np.inf, -np.inf], np.nan)
        return feats.fillna(feats.median()).fillna(0) if impute else feats

    @staticmethod
    def _run_autoencoder(X_train: np.ndarray, X_test: np.ndarray):
        """Uczy autoenkoder na X_train; zwraca błędy rekonstrukcji (train, test) – wyższy = bardziej anomalne."""
        # Skalowanie medianą i IQR: granica przycięcia odnosi się do typowego rozrzutu, nie zawyżonego przez anomalie
        scaler = RobustScaler().fit(X_train)
        X_train, X_test = scaler.transform(X_train), scaler.transform(X_test)

        # Lokalny stan RNG – deterministyczne wyniki bez wpływu na globalny seed
        with _TORCH_INIT_LOCK, torch.random.fork_rng():
            torch.manual_seed(42)
            autoencoder = TabularAutoencoder(X_train.shape[1])

        # Trening (na danych przyciętych) jest deterministyczny – pełny batch, bez losowości – więc może działać równolegle.
        # Ocena odbywa się na danych nieprzyciętych, więc skrajne wartości dają duży błąd rekonstrukcji.
        X_tensor = torch.FloatTensor(np.clip(X_train, -AE_TRAIN_CLIP, AE_TRAIN_CLIP))
        criterion = nn.MSELoss(reduction='none')
        optimizer = optim.Adam(autoencoder.parameters(), lr=0.01)

        # Lekki wariant treningu online dostosowany do pracy wewnątrz API
        for _ in range(100):
            optimizer.zero_grad()
            loss = criterion(autoencoder(X_tensor), X_tensor).mean()
            loss.backward()
            optimizer.step()

        autoencoder.eval()

        # Błąd rekonstrukcji każdej świecy uśredniony po cechach
        def errors(X: np.ndarray) -> np.ndarray:
            t = torch.FloatTensor(X)
            with torch.no_grad():
                return criterion(autoencoder(t), t).mean(dim=1).numpy()

        return errors(X_train), errors(X_test)

    @staticmethod
    def _fit_score(model_type: str, X_train: np.ndarray, X_test: np.ndarray, contamination: float, novelty: bool):
        """
        Uczy model na X_train i zwraca wyniki anomalii (train, test), gdzie wyższa wartość = silniejsza anomalia.
        novelty=False: X_test to te same punkty co X_train (tryb batch).
        """
        if model_type == 'isolation_forest':
            model = IsolationForest(random_state=42).fit(X_train)
            train, test = model.decision_function(X_train), model.decision_function(X_test)
        elif model_type == 'lof':
            model = LocalOutlierFactor(n_neighbors=min(20, len(X_train) - 1), novelty=novelty).fit(X_train)
            train = model.negative_outlier_factor_
            test = model.score_samples(X_test) if novelty else train
        elif model_type == 'ocsvm':
            model = OneClassSVM(nu=min(max(contamination, 0.01), 1.0), gamma='scale').fit(X_train)
            train, test = model.decision_function(X_train), model.decision_function(X_test)
        else:
            err_train, err_test = AnomalyDetector._run_autoencoder(X_train, X_test)
            # Autoenkoder zwraca błąd (wyższy = anomalia) – sprowadzamy do konwencji sklearn
            train, test = -err_train, -err_test

        # Konwencja sklearn: niższy score = bardziej anomalne; odwracamy znak
        return -np.asarray(train, dtype=float), -np.asarray(test, dtype=float)

    @staticmethod
    def _walk_forward(feats: pd.DataFrame, model_type: str, contamination: float):
        """
        Ocena bez wglądu w przyszłość: sesje [start, start + REFIT_EVERY) oceniane są modelem
        uczonym na wszystkich sesjach < start (okno rosnące). Imputacja, skalowanie i próg anomalii
        wyznaczane są wyłącznie z okna treningowego. Pierwsze MIN_TRAIN sesji nie jest oceniane.
        """
        n = len(feats)
        scores = np.full(n, np.nan)
        flags = np.zeros(n, dtype=bool)

        for start in range(WALK_FORWARD_MIN_TRAIN, n, WALK_FORWARD_REFIT_EVERY):
            end = min(start + WALK_FORWARD_REFIT_EVERY, n)
            train, test = feats.iloc[:start], feats.iloc[start:end]

            medians = train.median()
            train, test = train.fillna(medians).fillna(0), test.fillna(medians).fillna(0)

            # Ostatnia część okna treningowego służy do kalibracji progu: model jej nie widzi przy uczeniu,
            # więc jej wyniki są – tak jak wyniki nowych sesji – "spoza próby". Próg z wyników na danych
            # uczących byłby zaniżony (model ocenia znane punkty łagodniej) i oznaczał zbyt wiele anomalii.
            n_calib = max(WALK_FORWARD_MIN_CALIBRATION, int(len(train) * WALK_FORWARD_CALIBRATION_SHARE))
            fit_part, calib_part = train.iloc[:-n_calib], train.iloc[-n_calib:]
            scaler = StandardScaler().fit(fit_part)

            _, out_of_sample = AnomalyDetector._fit_score(
                model_type, scaler.transform(fit_part),
                scaler.transform(pd.concat([calib_part, test])), contamination, novelty=True)
            calib_scores, test_scores = out_of_sample[:n_calib], out_of_sample[n_calib:]

            # Sesja jest anomalią, jeśli jej wynik przekracza kwantyl (1 - contamination) wyników kalibracyjnych
            threshold = np.quantile(calib_scores, 1 - contamination)
            scores[start:end] = test_scores
            flags[start:end] = test_scores > threshold

        return scores, flags

    @staticmethod
    def flag_top_fraction(scores: np.ndarray, contamination: float) -> np.ndarray:
        """
        Oznacza jako anomalie dokładnie ceil(contamination * n) punktów o najwyższym wyniku.
        Wspólny próg dla wszystkich modeli – bez tego np. One-Class SVM (parametr nu jest tylko
        przybliżeniem) oznaczał więcej punktów niż pozostałe modele, co zaburzało porównanie.
        """
        n_flagged = min(len(scores), max(1, int(np.ceil(contamination * len(scores)))))
        flags = np.zeros(len(scores), dtype=bool)
        # Sortowanie stabilne: przy remisach wygrywa wcześniejszy punkt, liczba oznaczeń jest stała
        flags[np.argsort(-scores, kind='stable')[:n_flagged]] = True
        return flags

    @staticmethod
    def detect_anomalies(data: List[Dict[str, Any]], model_type: str = 'isolation_forest', contamination: float = 0.05,
                         mode: str = 'batch') -> List[Dict[str, Any]]:
        """
        Wykrywa anomalie za pomocą wybranego modelu (Isolation Forest, LOF, OCSVM, Autoencoder)
        na podstawie względnych cech cenowych, wolumenowych i wskaźników technicznych.
        W trybie 'walk_forward' sesje z okresu rozruchu mają anomaly_score = None i is_anomaly = False.
        """
        if model_type not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model_type: {model_type}")
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"Unsupported mode: {mode}")
        if not data:
            return []
        if mode == 'walk_forward' and len(data) <= WALK_FORWARD_MIN_TRAIN:
            raise ValueError(f"Walk-forward mode requires more than {WALK_FORWARD_MIN_TRAIN} data points.")

        df = pd.DataFrame(data)

        # Upewniamy się, że wszystkie wymagane kolumny techniczne istnieją (z bezpiecznymi wartościami domyślnymi)
        for col in ['ema_20', 'ema_50', 'sma_20', 'sma_50', 'bb_upper', 'bb_lower']:
            if col not in df.columns or df[col].isnull().all():
                df[col] = df['close']
        for col in ['volatility', 'returns', 'rsi', 'atr']:
            if col not in df.columns or df[col].isnull().all():
                df[col] = 0.0

        # Konwertujemy wszystkie kolumny liczbowe na float64, aby uniknąć problemów z typem object (None)
        numeric_cols = [
            'open', 'high', 'low', 'close', 'volume', 'returns', 'volatility',
            'sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal', 'ema_20', 'ema_50',
            'bb_upper', 'bb_lower', 'atr'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if mode == 'walk_forward':
            scores, flags = AnomalyDetector._walk_forward(
                AnomalyDetector.build_features(df, impute=False)[FEATURES], model_type, contamination)
        else:
            # Wspólne skalowanie danych dla wszystkich modeli (wymagane w OCSVM i LOF, przydatne opcjonalnie w IF)
            X_scaled = StandardScaler().fit_transform(AnomalyDetector.build_features(df)[FEATURES])
            _, scores = AnomalyDetector._fit_score(model_type, X_scaled, X_scaled, contamination, novelty=False)
            flags = AnomalyDetector.flag_top_fraction(scores, contamination)

        # anomaly_score: wyższa wartość = silniejsza anomalia
        df['anomaly_score'] = scores
        df['is_anomaly'] = flags

        # Sygnały transakcyjne (strategia konfluencji – oba warunki muszą być spełnione):
        # Kupno: RSI < 32 ORAZ cena poniżej dolnej wstęgi Bollingera
        # Sprzedaż: RSI > 68 ORAZ cena powyżej górnej wstęgi Bollingera
        df['signal'] = 'Hold'
        df.loc[(df['rsi'] < 32) & (df['close'] < df['bb_lower']), 'signal'] = 'Buy'
        df.loc[(df['rsi'] > 68) & (df['close'] > df['bb_upper']), 'signal'] = 'Sell'

        # Ograniczenie sygnałów do ostatnich SIGNAL_LOOKBACK_DAYS dni (sygnały historyczne nie są akcjonowalne)
        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'], errors='coerce')
            if dates.notna().any():
                cutoff_date = dates.max() - pd.Timedelta(days=SIGNAL_LOOKBACK_DAYS)
                df.loc[dates < cutoff_date, 'signal'] = 'Hold'

        # Wybór kolumn do zwrócenia
        valid_output_cols = [
            'date', 'open', 'high', 'low', 'close', 'volume',
            'returns', 'volatility', 'sma_20', 'sma_50',
            'rsi', 'macd', 'macd_signal', 'ema_20', 'ema_50',
            'bb_upper', 'bb_lower', 'atr', 'anomaly_score', 'is_anomaly', 'signal'
        ]
        available_cols = [c for c in valid_output_cols if c in df.columns]

        # Zastąpienie wartości NaN/Inf przez None dla poprawnej serializacji JSON
        df_out = df[available_cols].replace([np.inf, -np.inf], np.nan).astype(object)
        df_out = df_out.where(pd.notnull(df_out), None)

        return df_out.to_dict(orient='records')
