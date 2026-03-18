import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any

class AnomalyDetector:
    @staticmethod
    def detect_isolation_forest(data: List[Dict[str, Any]], contamination: float = 0.05) -> List[Dict[str, Any]]:
        """
        Wykrywa anomalie za pomocą Isolation Forest na podstawie stóp zwrotu i zmienności.
        """
        if not data:
            return []
            
        df = pd.DataFrame(data)
        
        # Upewnienie się, że mamy niezbędne cechy (RSI i ATR)
        required_features = ['returns', 'volatility', 'rsi', 'atr']
        
        # Uzupełnienie brakujących wartości (początkowe wiersze po obliczeniach kroczących)
        df_clean = df[required_features].fillna(0)
        
        # Inicjalizacja modelu Isolation Forest
        model = IsolationForest(contamination=contamination, random_state=42)
        
        # Trenowanie i predykcja
        model.fit(df_clean)
        df['anomaly_score'] = model.decision_function(df_clean)
        df['is_anomaly'] = model.predict(df_clean)
        
        # Mapowanie: -1 (anomalia) -> True, 1 (norma) -> False
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
