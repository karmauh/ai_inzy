from app.services.data_processor import DataProcessor
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any
import io
import contextlib

class MarketDataService:
    @staticmethod
    def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> List[Dict[str, Any]]:
        """
        Pobiera dane historyczne dla danego tickera (akcje lub krypto).
        """
        try:
            # Obiekt tickera yfinance i pobranie z wyciszeniem wyjścia
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval)
            
            if df.empty:
                return []
            
            # Resetowanie indeksu dla uzyskania daty jako kolumny i normalizacja nazw
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            
            # Weryfikacja wymaganych kolumn i ich filtrowanie
            valid_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            df = df[[c for c in valid_cols if c in df.columns]]
            
            # Dodanie wskaźników technicznych przez DataProcessor
            df = DataProcessor.add_technical_indicators(df)
            
            # Formatery dla serializacji JSON (daty i wartości NaN)
            if 'date' in df.columns:
                df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            df = df.astype(object).where(pd.notnull(df), None)
            
            return df.to_dict(orient='records')
            
        except Exception:
            # Obsługa błędów przy pobieraniu metadanych
            return []

    @staticmethod
    def get_asset_info(ticker: str) -> Dict[str, Any]:
        """
        Pobiera podstawowe informacje o aktywie i kluczowe statystyki.
        """
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                stock = yf.Ticker(ticker)
                info = stock.info
            
            # Ekstrakcja kluczowych wskaźników mikro/makro ekonomicznych
            return {
                "name": info.get("longName") or info.get("shortName"),
                "symbol": info.get("symbol"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "marketCap": info.get("marketCap"),
                "peRatio": info.get("trailingPE"),
                "dividendYield": info.get("dividendYield"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "currency": info.get("currency"),
                "description": info.get("longBusinessSummary"),
            }
        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
            return {}
