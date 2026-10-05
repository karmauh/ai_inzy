from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.market_data import MarketDataError, MarketDataService
from app.utils.ttl_cache import TTLCache


# --- TTLCache ---

def test_cache_expires_after_ttl():
    now = [0.0]
    cache = TTLCache(ttl_seconds=10, clock=lambda: now[0])
    cache.set("k", [1, 2])

    now[0] = 9.9
    assert cache.get("k") == [1, 2]
    now[0] = 10.1
    assert cache.get("k") is None


def test_cache_evicts_least_recently_used_entry():
    cache = TTLCache(ttl_seconds=100, max_entries=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.get("a")  # "a" używane ostatnio – usunięte zostanie "b"
    cache.set("c", 3)

    assert cache.get("a") == 1 and cache.get("c") == 3
    assert cache.get("b") is None


def test_cache_returns_copies():
    cache = TTLCache(ttl_seconds=100)
    cache.set("k", [{"close": 1.0}])
    cache.get("k")[0]["close"] = 999.0

    assert cache.get("k") == [{"close": 1.0}]


# --- MarketDataService ---

def _history_frame(n=60):
    dates = pd.date_range("2026-01-01", periods=n, tz="America/New_York", name="Date")
    close = pd.Series(range(100, 100 + n), index=dates, dtype=float)
    return pd.DataFrame({"Open": close, "High": close + 1, "Low": close - 1, "Close": close, "Volume": 1000.0})


def test_history_is_cached_per_symbol_and_period():
    ticker = MagicMock()
    ticker.history.return_value = _history_frame()
    with patch("app.services.market_data.yf.Ticker", return_value=ticker) as yf_ticker:
        first = MarketDataService.get_historical_data("msft", "1y")
        second = MarketDataService.get_historical_data("MSFT", "1y")
        MarketDataService.get_historical_data("MSFT", "2y")

    assert first == second and len(first) == 60
    assert yf_ticker.call_count == 2  # 1y z cache przy drugim wywołaniu, 2y to osobny wpis


def test_unknown_symbol_and_errors_are_not_cached():
    empty, failing = MagicMock(), MagicMock()
    empty.history.return_value = pd.DataFrame()
    failing.history.side_effect = RuntimeError("Yahoo down")
    with patch("app.services.market_data.yf.Ticker", side_effect=[empty, empty, failing]) as yf_ticker:
        assert MarketDataService.get_historical_data("NOPE") == []
        assert MarketDataService.get_historical_data("NOPE") == []
        with pytest.raises(MarketDataError):
            MarketDataService.get_historical_data("MSFT")

    assert yf_ticker.call_count == 3


def test_asset_info_cached_only_when_complete():
    broken, complete = MagicMock(), MagicMock()
    type(broken).info = property(lambda self: (_ for _ in ()).throw(RuntimeError("timeout")))
    complete.info = {"longName": "Microsoft Corporation", "symbol": "MSFT"}
    with patch("app.services.market_data.yf.Ticker", side_effect=[broken, complete]) as yf_ticker:
        assert MarketDataService.get_asset_info("MSFT")["name"] is None
        assert MarketDataService.get_asset_info("MSFT")["name"] == "Microsoft Corporation"
        assert MarketDataService.get_asset_info("MSFT")["name"] == "Microsoft Corporation"

    assert yf_ticker.call_count == 2
