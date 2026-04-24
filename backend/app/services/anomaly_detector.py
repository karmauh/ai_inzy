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
    def detect_anomalies(data: List[Dict[str, Any]], model_type: str = 'isolation_forest', contamination: float = 0.05) -> List[Dict[str, Any]]:
        """
        Wykrywa anomalie za pomocą wybranego modelu (Isolation Forest, LOF, OCSVM) na podstawie stóp zwrotu i zmienności.
        """
        if not data:
            return []
            
        df = pd.DataFrame(data)
        
        # --- FEATURE ENGINEERING ---
        
        # FAZA 1: Podstawowe nowe cechy wejściowe
        df['return_1d'] = df.get('close').pct_change(1)
        df['return_3d'] = df.get('close').pct_change(3)
        df['return_7d'] = df.get('close').pct_change(7)
        
        df['volume_change'] = df.get('volume').pct_change(1)
        df['volume_sma_20'] = df.get('volume').rolling(window=20).mean()
        
        # Cechy odległościowe i pozycyjne (bezpieczne przed dzieleniem przez 0)
        ema_20_safe = df.get('ema_20', df['close']).replace(0, np.nan)
        df['dist_to_ema20'] = (df['close'] - df.get('ema_20', df['close'])) / ema_20_safe
        
        bb_width = (df.get('bb_upper', df['close']) - df.get('bb_lower', df['close'])).replace(0, np.nan)
        df['bb_position'] = (df['close'] - df.get('bb_lower', df['close'])) / bb_width
        
        rolling_std_20 = df['close'].rolling(window=20).std().replace(0, np.nan)
        df['z_score_20'] = (df['close'] - df.get('sma_20', df['close'])) / rolling_std_20
        
        df['volatility_change'] = df.get('volatility').pct_change(1)
        
        # FAZA 2: Zaawansowane cechy (przygotowane pod kolejne etapy)
        df['momentum_5d'] = df['close'] - df['close'].shift(5)
        
        rolling_max = df['close'].cummax()
        df['drawdown'] = (df['close'] - rolling_max) / rolling_max.replace(0, np.nan)
        
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        
        # Dodanie wszystkich utworzonych cech do pipeline'u modeli
        required_features = [
            'returns', 'volatility', 'rsi', 'atr',
            'return_1d', 'return_3d', 'return_7d',
            'volume_change', 'volume_sma_20',
            'dist_to_ema20', 'bb_position', 'z_score_20', 'volatility_change',
            'momentum_5d', 'drawdown', 'body', 'upper_shadow', 'lower_shadow'
        ]
        
        # Obsługa wartości skrajnych, a następnie uzupełnienie brakujących wartości powieleniem lub zerem
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        # Używamy ffill żeby ewentualnie przeciągnąć w dół, a resztę dociąć zerem
        df_clean = df[required_features].ffill().fillna(0)
        
        # Wspólne skalowanie danych dla wszystkich modeli (wymagane w OCSVM i LOF, przydatne opcjonalnie w IF)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_clean)
        
        if model_type == 'isolation_forest':
            model = IsolationForest(contamination=contamination, random_state=42)
            model.fit(X_scaled)
            df['anomaly_score'] = model.decision_function(X_scaled)
            df['is_anomaly'] = model.predict(X_scaled)
        elif model_type == 'lof':
            model = LocalOutlierFactor(contamination=contamination)
            df['is_anomaly'] = model.fit_predict(X_scaled)
            df['anomaly_score'] = model.negative_outlier_factor_
        elif model_type == 'ocsvm':
            nu = min(max(contamination, 0.01), 1.0)
            model = OneClassSVM(nu=nu, gamma='scale')
            model.fit(X_scaled)
            df['anomaly_score'] = model.decision_function(X_scaled)
            df['is_anomaly'] = model.predict(X_scaled)
        elif model_type == 'autoencoder':
            # Architektura tablicowa z użyciem Torch Tensor
            X_tensor = torch.FloatTensor(X_scaled)
            input_dim = X_tensor.shape[1]
            
            autoencoder = TabularAutoencoder(input_dim)
            criterion = nn.MSELoss(reduction='none') 
            optimizer = optim.Adam(autoencoder.parameters(), lr=0.01)
            
            # Lekki wariant treningu online dostosowany do pracy wewnatrz API
            epochs = 100
            for epoch in range(epochs):
                optimizer.zero_grad()
                outputs = autoencoder(X_tensor)
                loss = criterion(outputs, X_tensor).mean() # Uczymy sie sredniego bledu
                loss.backward()
                optimizer.step()
                
            autoencoder.eval()
            with torch.no_grad():
                reconstructed = autoencoder(X_tensor)
                # Obliczanie bledu rekonstrukcji kazdej swiecy per cecha
                errors = criterion(reconstructed, X_tensor).mean(dim=1).numpy()
                
            # Konwencja w obiekcie wsprocesujacym zaklada odwrócenie znaku na koncu,
            # wiec sztucznie mnozymy wynik autoenkodera przez -1 by w systemie 
            # wyjsciowym z powrotem byc dodatnim rozkladem bledow.
            df['anomaly_score'] = -errors
            
            # Wymuszenie binarnej flagi 1 / -1
            threshold = np.percentile(errors, 100 * (1 - contamination))
            df['is_anomaly'] = np.where(errors >= threshold, -1, 1)
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")
            
        # Ujednolicenie skali score'a: modele zwracają mniejsze/ujemne wartości dla anomalii. 
        # Odwracamy znak, by większa wartość oznaczała "silniejszą" anomalię.
        df['anomaly_score'] = -df['anomaly_score']
        
        # Wspólne mapowanie wyniku binarnego we wszystkich modelach: -1 (anomalia) -> True, 1 (norma) -> False
        df['is_anomaly'] = df['is_anomaly'].apply(lambda x: True if x == -1 else False)
        
        # Generowanie sygnałów transakcyjnych na podstawie wskaźników (Strategia Konfluencji)
        df['signal'] = 'Hold'
        
        # Sygnał Kupna: RSI < 32 i cena poniżej dolnej wstęgi Bollingera
        buy_condition = (df['rsi'] < 32) & (df['close'] < df['bb_lower'])
        
        # Sygnał Sprzedaży: RSI > 68 lub cena powyżej górnej wstęgi Bollingera
        sell_condition = (df['rsi'] > 68) & (df['close'] > df['bb_upper'])
        
        df.loc[buy_condition, 'signal'] = 'Buy'
        df.loc[sell_condition, 'signal'] = 'Sell'
        
        # Filtrowanie dat: ograniczenie sygnałów 'Buy' do ostatnich 2 miesięcy
        
        try:
            if not pd.api.types.is_datetime64_any_dtype(df['date']):
                df['date'] = pd.to_datetime(df['date'])
                
            max_date = df['date'].max()
            cutoff_date = max_date - pd.Timedelta(days=60)
            
            # Maskowanie przestarzałych sygnałów 'Buy' powyżej dwóch miesięcy
            mask_old = df['date'] < cutoff_date
            df.loc[mask_old & (df['signal'] == 'Buy'), 'signal'] = 'Hold'
            
        except Exception:
            # Obsługa błędu przy filtrowaniu dat
            pass

        # Wybór kolumn do zwrócenia (zgodnie ze schematem StockDataPoint)
        valid_output_cols = [
            'date', 'open', 'high', 'low', 'close', 'volume', 
            'returns', 'volatility', 'sma_20', 'sma_50', 
            'rsi', 'macd', 'macd_signal', 'ema_20', 'ema_50', 
            'bb_upper', 'bb_lower', 'atr', 'anomaly_score', 'is_anomaly', 'signal'
        ]
        available_cols = [c for c in valid_output_cols if c in df.columns]
        
        # Zastąpienie wartości NaN/Inf dla poprawnej serializacji JSON
        df_out = df[available_cols].replace([np.inf, -np.inf], np.nan)
        
        # Konwersja formatu daty na tekst przed zwrotem danych
             
        df_out = df_out.where(pd.notnull(df_out), None)
        
        return df_out.to_dict(orient='records')
