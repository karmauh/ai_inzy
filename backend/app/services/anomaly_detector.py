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
from typing import List, Dict, Any, Optional

BASE_MODELS = ('isolation_forest', 'lof', 'ocsvm', 'autoencoder')
# 'ensemble' – średnia odpornych z-score'ów wyników wszystkich modeli bazowych.
# Wybrany eksperymentalnie (6 spółek x 5 przebiegów, 2 scenariusze x 2 tryby) spośród średniej/maksimum rang
# i średniej z-score'ów dla różnych zestawów modeli: średnie F1 0.549 wobec 0.536 najlepszego pojedynczego modelu
# (LOF), a w najtrudniejszym warunku (scenariusz rozszerzony, walk-forward) 0.325 wobec 0.298.
SUPPORTED_MODELS = BASE_MODELS + ('ensemble',)
ENSEMBLE_MEMBERS = BASE_MODELS

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
# Limit douczeń na analizę – przy długich okresach (np. 5 lat) model douczany jest rzadziej niż co 10 sesji,
# aby czas obliczeń nie rósł liniowo z długością historii
WALK_FORWARD_MAX_REFITS = 40
# Część okna treningowego (najnowsze sesje) odkładana do kalibracji progu anomalii
WALK_FORWARD_CALIBRATION_SHARE = 0.3
WALK_FORWARD_MIN_CALIBRATION = 20

# Sygnały starsze niż tyle dni od ostatniej sesji są wygaszane do 'Hold'
SIGNAL_LOOKBACK_DAYS = 60
# Klasyczne progi RSI (Wilder, 1978): wyprzedanie < 30, wykupienie > 70
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Wyjaśnienia anomalii: cechy porównywane z poprzednimi EXPLANATION_WINDOW sesjami (bez sesji ocenianej)
EXPLANATION_WINDOW = 120
EXPLANATION_MIN_HISTORY = 20
EXPLANATION_TOP_FEATURES = 3
# 'returns' to ta sama wartość co 'return_1d' – pomijamy duplikat w wyjaśnieniach
EXPLANATION_EXCLUDED = {'returns'}

# Bez 'returns' (= 'return_1d') i 'z_score_20' (bb_position = 0,5 + z_score_20 / 4) – zdublowana cecha
# miałaby podwójną wagę w odległościach (LOF, OCSVM) i byłaby dwa razy częściej losowana w Isolation Forest
FEATURES = [
    'volatility', 'rsi', 'atr',
    'return_1d', 'return_3d', 'return_7d',
    'volume_change', 'volume_ratio',
    'dist_to_ema20', 'bb_position', 'volatility_change',
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
    def _robust_z(scores: np.ndarray, reference: np.ndarray) -> np.ndarray:
        """
        Odporny z-score (mediana i rozstęp międzykwartylowy) względem wyników referencyjnych
        (tryb batch: wszystkie punkty, walk-forward: punkty kalibracyjne z przeszłości).
        Sprowadza wyniki modeli o różnych skalach do wspólnej skali przed uśrednieniem.
        """
        q1, median, q3 = np.quantile(reference, [0.25, 0.5, 0.75])
        return (scores - median) / ((q3 - q1) or 1.0)

    @staticmethod
    def _fit_score(model_type: str, X_train: np.ndarray, X_test: np.ndarray, contamination: float, novelty: bool,
                   n_reference: Optional[int] = None):
        """
        Uczy model na X_train i zwraca wyniki anomalii (train, test), gdzie wyższa wartość = silniejsza anomalia.
        novelty=False: X_test to te same punkty co X_train (tryb batch).
        n_reference (tylko ensemble): liczba początkowych wierszy X_test, względem których normalizowane są
        wyniki modeli bazowych – w walk-forward są to sesje kalibracyjne, więc łączenie nie zagląda w przyszłość.
        """
        if model_type == 'ensemble':
            reference = slice(0, n_reference)
            ensemble = np.mean([
                AnomalyDetector._robust_z(test, test[reference])
                for _, test in (AnomalyDetector._fit_score(m, X_train, X_test, contamination, novelty) for m in ENSEMBLE_MEMBERS)
            ], axis=0)
            # Wynik treningowy nie jest używany przez ensemble (próg liczony jest z wyników testowych/kalibracyjnych)
            return np.full(len(X_train), np.nan), ensemble

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
    def walk_forward_refit_interval(n: int) -> int:
        """Co ile sesji douczany jest model w trybie walk-forward dla szeregu długości n."""
        return max(WALK_FORWARD_REFIT_EVERY, int(np.ceil((n - WALK_FORWARD_MIN_TRAIN) / WALK_FORWARD_MAX_REFITS)))

    @staticmethod
    def _walk_forward(feats: pd.DataFrame, model_type: str, contamination: float):
        """
        Ocena bez wglądu w przyszłość: sesje [start, start + refit_every) oceniane są modelem
        uczonym na wszystkich sesjach < start (okno rosnące). Imputacja, skalowanie i próg anomalii
        wyznaczane są wyłącznie z okna treningowego. Pierwsze MIN_TRAIN sesji nie jest oceniane.
        """
        n = len(feats)
        scores = np.full(n, np.nan)
        flags = np.zeros(n, dtype=bool)
        refit_every = AnomalyDetector.walk_forward_refit_interval(n)

        for start in range(WALK_FORWARD_MIN_TRAIN, n, refit_every):
            end = min(start + refit_every, n)
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
                scaler.transform(pd.concat([calib_part, test])), contamination, novelty=True, n_reference=n_calib)
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
    def explain(feats: pd.DataFrame, rows: np.ndarray) -> Dict[int, List[Dict[str, Any]]]:
        """
        Dla wskazanych sesji zwraca cechy najbardziej odbiegające od normy – odporny z-score względem
        mediany i rozstępu międzykwartylowego z poprzednich EXPLANATION_WINDOW sesji (bez sesji ocenianej,
        więc wyjaśnienie nie korzysta z przyszłości). Mechanizm jest niezależny od modelu: opisuje, co było
        nietypowe w danej sesji, a nie wewnętrzne działanie konkretnego algorytmu.
        """
        candidates = [c for c in feats.columns if c not in EXPLANATION_EXCLUDED]
        history = feats[candidates].rolling(EXPLANATION_WINDOW, min_periods=EXPLANATION_MIN_HISTORY)
        median = history.median().shift(1)
        iqr = (history.quantile(0.75) - history.quantile(0.25)).shift(1).replace(0, np.nan)
        z = (feats[candidates] - median) / iqr

        explanations = {}
        for row in rows:
            top = z.iloc[row].dropna().abs().sort_values(ascending=False).head(EXPLANATION_TOP_FEATURES)
            explanations[int(row)] = [
                {
                    "feature": feature,
                    "value": float(feats.iloc[row][feature]),
                    "typical": float(median.iloc[row][feature]),
                    "z": float(z.iloc[row][feature]),
                }
                for feature in top.index
            ]
        return explanations

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

        raw_features = AnomalyDetector.build_features(df, impute=False)[FEATURES]
        if mode == 'walk_forward':
            scores, flags = AnomalyDetector._walk_forward(raw_features, model_type, contamination)
        else:
            # Wspólne skalowanie danych dla wszystkich modeli (wymagane w OCSVM i LOF, przydatne opcjonalnie w IF)
            X_scaled = StandardScaler().fit_transform(AnomalyDetector.build_features(df)[FEATURES])
            _, scores = AnomalyDetector._fit_score(model_type, X_scaled, X_scaled, contamination, novelty=False)
            flags = AnomalyDetector.flag_top_fraction(scores, contamination)

        # anomaly_score: wyższa wartość = silniejsza anomalia
        df['anomaly_score'] = scores
        df['is_anomaly'] = flags

        # Wyjaśnienia tylko dla sesji oznaczonych jako anomalie (pozostałe: None – mniejsza odpowiedź API)
        explanations = AnomalyDetector.explain(raw_features, np.flatnonzero(flags))
        df['explanation'] = [explanations.get(i) for i in range(len(df))]

        # Sygnały transakcyjne (strategia konfluencji – oba warunki muszą być spełnione):
        # Kupno: RSI < RSI_OVERSOLD ORAZ cena poniżej dolnej wstęgi Bollingera
        # Sprzedaż: RSI > RSI_OVERBOUGHT ORAZ cena powyżej górnej wstęgi Bollingera
        df['signal'] = 'Hold'
        df.loc[(df['rsi'] < RSI_OVERSOLD) & (df['close'] < df['bb_lower']), 'signal'] = 'Buy'
        df.loc[(df['rsi'] > RSI_OVERBOUGHT) & (df['close'] > df['bb_upper']), 'signal'] = 'Sell'

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
            'bb_upper', 'bb_lower', 'atr', 'anomaly_score', 'is_anomaly', 'signal', 'explanation'
        ]
        available_cols = [c for c in valid_output_cols if c in df.columns]

        # Zastąpienie wartości NaN/Inf przez None dla poprawnej serializacji JSON
        df_out = df[available_cols].replace([np.inf, -np.inf], np.nan).astype(object)
        df_out = df_out.where(pd.notnull(df_out), None)

        return df_out.to_dict(orient='records')
