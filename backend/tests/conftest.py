import numpy as np
import pandas as pd
import pytest

from app.services.data_processor import DataProcessor


def make_market_data(n: int = 250, seed: int = 0):
    """Syntetyczne notowania (błądzenie losowe) przetworzone tak jak w MarketDataService."""
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.015, n)))
    df = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=n).strftime('%Y-%m-%d'),
        'open': close * (1 + rng.normal(0, 0.003, n)),
        'high': close * 1.01,
        'low': close * 0.99,
        'close': close,
        'volume': rng.integers(1_000_000, 2_000_000, n).astype(float),
    })
    df = DataProcessor.add_technical_indicators(df)
    return df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')


@pytest.fixture
def market_data():
    return make_market_data()
