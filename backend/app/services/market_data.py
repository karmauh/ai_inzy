from app.services.data_processor import DataProcessor
from app.utils.ttl_cache import TTLCache
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any
import io
import contextlib
import logging

logger = logging.getLogger(__name__)
# yfinance loguje nieznane symbole jako ERROR – to oczekiwany przypadek (404), nie błąd aplikacji
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# Cache odpowiedzi Yahoo Finance: mniej zapytań (Yahoo ogranicza ich liczbę) i szybsze ponowne wyszukiwania.
# Notowania dzienne zmieniają się w trakcie sesji, więc żyją krócej niż metadane spółki.
# Puste wyniki (nieznany symbol) i błędy nie są zapisywane.
HISTORY_CACHE = TTLCache(ttl_seconds=15 * 60, max_entries=64)
INFO_CACHE = TTLCache(ttl_seconds=24 * 60 * 60, max_entries=256)


class MarketDataError(Exception):
    """Błąd komunikacji ze źródłem danych rynkowych (sieć, limit zapytań itp.)."""


class MarketDataService:
    @staticmethod
    def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> List[Dict[str, Any]]:
        """
        Pobiera dane historyczne dla danego tickera (akcje lub krypto).
        Zwraca pustą listę, gdy symbol nie istnieje; rzuca MarketDataError przy błędzie źródła danych.
        """
        cache_key = (ticker.upper(), period, interval)
        cached = HISTORY_CACHE.get(cache_key)
        if cached is not None:
            return cached

        try:
            # Obiekt tickera yfinance i pobranie z wyciszeniem wyjścia
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                df = yf.Ticker(ticker).history(period=period, interval=interval)
        except Exception as e:
            logger.exception("Błąd pobierania danych historycznych dla %s", ticker)
            raise MarketDataError(str(e)) from e

        if df is None or df.empty:
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
            df['date'] = pd.to_datetime(df['date'], utc=True).dt.strftime('%Y-%m-%d')

        df = df.astype(object).where(pd.notnull(df), None)

        records = df.to_dict(orient='records')
        HISTORY_CACHE.set(cache_key, records)
        return records

    @staticmethod
    def get_asset_info(ticker: str) -> Dict[str, Any]:
        """
        Pobiera podstawowe informacje o aktywie i kluczowe statystyki.
        Brak metadanych nie jest błędem krytycznym – zwracany jest wtedy sam symbol.
        """
        cache_key = ticker.upper()
        cached = INFO_CACHE.get(cache_key)
        if cached is not None:
            return cached

        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                info = yf.Ticker(ticker).info or {}
        except Exception:
            logger.warning("Nie udało się pobrać metadanych dla %s", ticker, exc_info=True)
            info = {}

        result = {
            "name": info.get("longName") or info.get("shortName"),
            "symbol": info.get("symbol") or ticker,
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
        # Zapisujemy tylko pełne metadane – przy błędzie spróbujemy ponownie przy następnym zapytaniu
        if info:
            INFO_CACHE.set(cache_key, result)
        return result
