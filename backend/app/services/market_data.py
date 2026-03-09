from app.services.data_processor import DataProcessor
import numpy as np
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any

class MarketDataService:
    @staticmethod
    def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> List[Dict[str, Any]]:
        """
        Pobiera dane historyczne dla danego tickera (akcje lub krypto).
        """
        try:
            # Obiekt tickera yfinance
            stock = yf.Ticker(ticker)
            
            # Pobieranie historii notowań
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                return []
            
            # Resetowanie indeksu dla uzyskania daty jako kolumny i normalizacja nazw
            
            # Weryfikacja wymaganych kolumn i ich filtrowanie
            df = df[valid_cols]
            
            # Dodanie wskaźników technicznych przez DataProcessor
            df = DataProcessor.add_technical_indicators(df)
            
            # Formatery dla serializacji JSON (daty i wartości NaN)
            df = df.astype(object).where(pd.notnull(df), None)
            
            return df.to_dict(orient='records')
            
            # Obsługa błędu pobierania danych
            return []

    @staticmethod
    def get_asset_info(ticker: str) -> Dict[str, Any]:
        """
        Pobiera podstawowe informacje o aktywie i kluczowe statystyki.
        """
        try:
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
