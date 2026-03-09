import pandas as pd
import numpy as np
from fastapi import UploadFile, HTTPException
from io import BytesIO
from app.models.schemas import StockDataPoint
from typing import List, Dict, Any

class DataProcessor:
    @staticmethod
    async def process_csv_upload(file: UploadFile) -> Dict[str, Any]:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
        
        try:
            contents = await file.read()
            df = pd.read_csv(BytesIO(contents))
            
            # Normalizacja nazw kolumn do małych liter
            df.columns = df.columns.str.lower()
            
            # Sprawdzenie wymaganych kolumn
            required_columns = {'date', 'open', 'high', 'low', 'close', 'volume'}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")
            
            # Konwersja daty na obiekt datetime i sortowanie
            
            # Podstawowe informacje o danych
            total_rows = len(df)
            start_date = df['date'].min().strftime('%Y-%m-%d')
            end_date = df['date'].max().strftime('%Y-%m-%d')
            
            # Obliczanie wskaźników technicznych
            df = DataProcessor.add_technical_indicators(df)
            
            # Tworzenie podglądu (pierwsze 5 wierszy) z obsługą wartości pustych dla JSON
            df_preview = df.head(5).astype(object).where(pd.notnull(df.head(5)), None)
            preview_data = df_preview.to_dict(orient='records')
            
            return {
                "filename": file.filename,
                "total_rows": total_rows,
                "daterange_start": start_date,
                "daterange_end": end_date,
                "preview": preview_data,
                "message": "File processed successfully with technical indicators"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

        return df
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Oblicza wskaźniki techniczne:
        - Dzienne stopy zwrotu
        - Zmienność (20-dniowe odchylenie standardowe)
        - Średnie kroczące SMA (20 i 50-dniowe)
        - RSI (wskaźnik siły względnej, 14-dniowy)
        - MACD (12-26-9)
        - EMA (20 i 50-dniowe)
        - Wstęgi Bollingera
        - ATR (Average True Range)
        """
        # Dzienne stopy zwrotu i zmienność
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['close'].rolling(window=20).std()
        
        # Średnie kroczące SMA (20 i 50-dniowe)
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Wskaźnik siły względnej (RSI 14-dniowy)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        # Wskaźnik MACD i EMA
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Średnie wykładnicze EMA (e.g., 20 i 50)
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # Wstęgi Bollingera (20-dniowe, 2 odchylenia standardowe)
        df['bb_upper'] = df['sma_20'] + (2 * df['volatility'])
        df['bb_lower'] = df['sma_20'] - (2 * df['volatility'])
        
        # Wskaźnik ATR (Average True Range, 14-dniowy)
        prev_close = df['close'].shift(1)
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - prev_close).abs()
        tr3 = (df['low'] - prev_close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        return df
