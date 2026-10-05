import pytest
from app.services.anomaly_detector import AnomalyDetector
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    return [
        {
            'date': f'2026-04-{i:02d}', 
            'open': 100 + i, 
            'high': 105 + i, 
            'low': 95 + i, 
            'close': 100 + i, 
            'volume': 1000 + i * 10, 
            'returns': 0.01 * (i % 3), 
            'volatility': 0.02 * (i % 2 + 1), 
            'rsi': 50 + i, 
            'atr': 5 + i * 0.1, 
            'bb_upper': 110 + i, 
            'bb_lower': 90 + i,
            'macd': 0.1,
            'macd_signal': 0.05,
            'ema_20': 100.5,
            'ema_50': 100.1,
            'sma_20': 100.0,
            'sma_50': 99.0
        }
        for i in range(1, 21)
    ]

@pytest.mark.parametrize("model_type", ["isolation_forest", "lof", "ocsvm", "autoencoder"])
def test_detect_anomalies_all_models(sample_data, model_type):
    # Dodajemy jeden punkt jako wyraźną anomalię (np. duży spadek wykraczający poza typowe wahania)
    outlier = sample_data[-1].copy()
    outlier['returns'] = -0.5
    outlier['volatility'] = 0.9
    outlier['rsi'] = 10
    sample_data.append(outlier)
    
    results = AnomalyDetector.detect_anomalies(sample_data, model_type=model_type, contamination=0.1)
    
    # Podstawowe testy integralności
    assert isinstance(results, list)
    assert len(results) == len(sample_data)
    
    # Test formatu wyjściowego
    for res in results:
        assert 'is_anomaly' in res
        assert 'anomaly_score' in res
        assert 'signal' in res
        assert isinstance(res['is_anomaly'], bool)
        
        # Test na brak NaN po pre-processingu i detekcji
        assert res['anomaly_score'] is not None

def test_detect_anomalies_empty_data():
    results = AnomalyDetector.detect_anomalies([], model_type="isolation_forest")
    assert results == []

def test_detect_anomalies_unsupported_model(sample_data):
    with pytest.raises(ValueError):
        AnomalyDetector.detect_anomalies(sample_data, model_type="unsupported")


@pytest.mark.parametrize("model_type", ["isolation_forest", "lof", "autoencoder"])
def test_warmup_period_is_not_flagged_disproportionately(model_type):
    # Wskaźniki są puste w pierwszych ~50 sesjach; nie mogą one dominować wśród anomalii
    from tests.conftest import make_market_data
    flagged, flagged_early = 0, 0
    for seed in range(3):
        results = AnomalyDetector.detect_anomalies(make_market_data(seed=seed), model_type=model_type, contamination=0.05)
        idx = [i for i, r in enumerate(results) if r['is_anomaly']]
        flagged += len(idx)
        flagged_early += sum(i < 50 for i in idx)

    # 50/250 = 20% danych – dopuszczamy losowe odchylenie, ale nie 50%+ jak przy imputacji zerem
    assert flagged_early / flagged < 0.35


def test_autoencoder_is_deterministic(market_data):
    first = AnomalyDetector.detect_anomalies(market_data, model_type="autoencoder")
    second = AnomalyDetector.detect_anomalies(market_data, model_type="autoencoder")

    assert [r['anomaly_score'] for r in first] == [r['anomaly_score'] for r in second]


def test_signals_require_both_conditions_and_recent_dates(sample_data):
    # Ostatnia sesja: RSI wykupione ORAZ cena nad górną wstęgą -> Sell
    sample_data[-1].update({'rsi': 80, 'close': 200, 'bb_upper': 150})
    # Przedostatnia: tylko RSI wykupione -> Hold
    sample_data[-2].update({'rsi': 80})
    # Bardzo stara sesja spełniająca warunki kupna -> wygaszona do Hold
    sample_data[0].update({'date': '2025-01-01', 'rsi': 10, 'close': 50, 'bb_lower': 60})

    results = AnomalyDetector.detect_anomalies(sample_data, model_type="isolation_forest")

    assert results[-1]['signal'] == 'Sell'
    assert results[-2]['signal'] == 'Hold'
    assert results[0]['signal'] == 'Hold'
    assert results[0]['date'] == '2025-01-01'
