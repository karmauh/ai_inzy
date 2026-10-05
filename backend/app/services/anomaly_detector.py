import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any

SUPPORTED_MODELS = ('isolation_forest', 'lof', 'ocsvm', 'autoencoder')

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
    def build_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Buduje macierz cech dla modeli. Wszystkie cechy są względne (niezależne od skali ceny/wolumenu).
        Braki z okresu rozgrzewki wskaźników (pierwsze ~20 sesji) uzupełniane są medianą cechy,
        aby nie tworzyć sztucznych wartości skrajnych (np. RSI = 0), które modele uznałyby za anomalie.
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
        return feats.fillna(feats.median()).fillna(0)

    @staticmethod
    def _run_autoencoder(X_scaled: np.ndarray, contamination: float):
        # Lokalny stan RNG – deterministyczne wyniki bez wpływu na globalny seed
        with torch.random.fork_rng():
            torch.manual_seed(42)
            X_tensor = torch.FloatTensor(X_scaled)
            autoencoder = TabularAutoencoder(X_tensor.shape[1])
            criterion = nn.MSELoss(reduction='none')
            optimizer = optim.Adam(autoencoder.parameters(), lr=0.01)

            # Lekki wariant treningu online dostosowany do pracy wewnątrz API
            for _ in range(100):
                optimizer.zero_grad()
                loss = criterion(autoencoder(X_tensor), X_tensor).mean()
                loss.backward()
                optimizer.step()

            autoencoder.eval()
            with torch.no_grad():
                # Błąd rekonstrukcji każdej świecy uśredniony po cechach
                errors = criterion(autoencoder(X_tensor), X_tensor).mean(dim=1).numpy()

        threshold = np.percentile(errors, 100 * (1 - contamination))
        # Konwencja sklearn: niższy score = bardziej anomalne, -1 = anomalia
        return -errors, np.where(errors >= threshold, -1, 1)

    @staticmethod
    def detect_anomalies(data: List[Dict[str, Any]], model_type: str = 'isolation_forest', contamination: float = 0.05) -> List[Dict[str, Any]]:
        """
        Wykrywa anomalie za pomocą wybranego modelu (Isolation Forest, LOF, OCSVM, Autoencoder)
        na podstawie względnych cech cenowych, wolumenowych i wskaźników technicznych.
        """
        if model_type not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model_type: {model_type}")
        if not data:
            return []

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

        # Wspólne skalowanie danych dla wszystkich modeli (wymagane w OCSVM i LOF, przydatne opcjonalnie w IF)
        X_scaled = StandardScaler().fit_transform(AnomalyDetector.build_features(df)[FEATURES])

        if model_type == 'isolation_forest':
            model = IsolationForest(contamination=contamination, random_state=42)
            model.fit(X_scaled)
            scores, labels = model.decision_function(X_scaled), model.predict(X_scaled)
        elif model_type == 'lof':
            model = LocalOutlierFactor(n_neighbors=min(20, len(df) - 1), contamination=contamination)
            labels = model.fit_predict(X_scaled)
            scores = model.negative_outlier_factor_
        elif model_type == 'ocsvm':
            model = OneClassSVM(nu=min(max(contamination, 0.01), 1.0), gamma='scale')
            model.fit(X_scaled)
            scores, labels = model.decision_function(X_scaled), model.predict(X_scaled)
        else:
            scores, labels = AnomalyDetector._run_autoencoder(X_scaled, contamination)

        # Ujednolicenie skali score'a: modele zwracają mniejsze/ujemne wartości dla anomalii.
        # Odwracamy znak, by większa wartość oznaczała "silniejszą" anomalię.
        df['anomaly_score'] = -np.asarray(scores, dtype=float)
        # Wspólne mapowanie wyniku binarnego: -1 (anomalia) -> True, 1 (norma) -> False
        df['is_anomaly'] = np.asarray(labels) == -1

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
