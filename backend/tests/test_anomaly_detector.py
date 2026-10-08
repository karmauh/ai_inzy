from unittest.mock import patch
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

@pytest.mark.parametrize("model_type", ["isolation_forest", "lof", "ocsvm", "autoencoder", "ensemble"])
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


@pytest.mark.parametrize("model_type", ["isolation_forest", "lof", "autoencoder", "ensemble"])
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


def test_signals_use_classic_rsi_thresholds(sample_data):
    from app.services.anomaly_detector import RSI_OVERSOLD, RSI_OVERBOUGHT
    assert (RSI_OVERSOLD, RSI_OVERBOUGHT) == (30, 70)

    # Cena poza wstęgą we wszystkich czterech sesjach – o sygnale decyduje wyłącznie próg RSI
    sample_data[-4].update({'rsi': 29, 'close': 50, 'bb_lower': 60})
    sample_data[-3].update({'rsi': 31, 'close': 50, 'bb_lower': 60})
    sample_data[-2].update({'rsi': 71, 'close': 200, 'bb_upper': 150})
    sample_data[-1].update({'rsi': 69, 'close': 200, 'bb_upper': 150})

    results = AnomalyDetector.detect_anomalies(sample_data, model_type="isolation_forest")

    assert [r['signal'] for r in results[-4:]] == ['Buy', 'Hold', 'Sell', 'Hold']


@pytest.mark.parametrize("model_type", ["isolation_forest", "lof", "ocsvm", "autoencoder", "ensemble"])
@pytest.mark.parametrize("contamination", [0.01, 0.05, 0.2])
def test_all_models_flag_the_same_fraction(market_data, model_type, contamination):
    # Wspólny próg – porównanie precision/recall między modelami jest uczciwe
    results = AnomalyDetector.detect_anomalies(market_data, model_type=model_type, contamination=contamination)

    assert sum(r['is_anomaly'] for r in results) == int(np.ceil(contamination * len(market_data)))


def test_flagged_points_have_highest_scores(market_data):
    results = AnomalyDetector.detect_anomalies(market_data, model_type="ocsvm", contamination=0.05)
    flagged = [r['anomaly_score'] for r in results if r['is_anomaly']]
    normal = [r['anomaly_score'] for r in results if not r['is_anomaly']]

    assert min(flagged) >= max(normal)


# --- Tryb walk-forward (bez wglądu w przyszłość) ---

@pytest.mark.parametrize("model_type", ["isolation_forest", "lof", "ocsvm", "autoencoder", "ensemble"])
def test_walk_forward_does_not_look_ahead(market_data, model_type):
    # Zmiana przyszłych notowań nie może zmienić oceny wcześniejszych sesji
    cut = 150
    altered = [dict(row) for row in market_data]
    for row in altered[cut:]:
        row.update({'close': row['close'] * 3, 'volume': row['volume'] * 10})

    original = AnomalyDetector.detect_anomalies(market_data, model_type=model_type, mode="walk_forward")
    changed = AnomalyDetector.detect_anomalies(altered, model_type=model_type, mode="walk_forward")

    assert [r['anomaly_score'] for r in original[:cut]] == [r['anomaly_score'] for r in changed[:cut]]
    assert [r['is_anomaly'] for r in original[:cut]] == [r['is_anomaly'] for r in changed[:cut]]


def test_walk_forward_skips_warmup_period(market_data):
    from app.services.anomaly_detector import WALK_FORWARD_MIN_TRAIN
    results = AnomalyDetector.detect_anomalies(market_data, model_type="lof", mode="walk_forward")

    assert all(r['anomaly_score'] is None and not r['is_anomaly'] for r in results[:WALK_FORWARD_MIN_TRAIN])
    assert all(r['anomaly_score'] is not None for r in results[WALK_FORWARD_MIN_TRAIN:])
    assert any(r['is_anomaly'] for r in results)


def test_walk_forward_requires_enough_data(sample_data):
    with pytest.raises(ValueError, match="Walk-forward"):
        AnomalyDetector.detect_anomalies(sample_data, model_type="lof", mode="walk_forward")


def test_batch_mode_is_default_and_unchanged(market_data):
    default = AnomalyDetector.detect_anomalies(market_data, model_type="isolation_forest")
    batch = AnomalyDetector.detect_anomalies(market_data, model_type="isolation_forest", mode="batch")

    assert default == batch


@pytest.mark.parametrize("mode", ["batch", "walk_forward"])
def test_autoencoder_flags_obvious_spike(mode):
    # Autoenkoder uczony bez przycięcia wartości skrajnych "uczył się" je odtwarzać i przeoczał wyraźne anomalie
    from tests.conftest import make_market_data
    from app.services.data_processor import DataProcessor
    data = make_market_data(seed=3)
    spike = 200
    df = pd.DataFrame(data)
    df.loc[spike, ['close', 'high']] = df.loc[spike, 'close'] * 1.3
    df.loc[spike, 'volume'] = df.loc[spike, 'volume'] * 8
    df = DataProcessor.add_technical_indicators(df[['date', 'open', 'high', 'low', 'close', 'volume']].astype({'close': float, 'high': float, 'volume': float}))
    data = df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')

    results = AnomalyDetector.detect_anomalies(data, model_type="autoencoder", contamination=0.05, mode=mode)

    assert results[spike]['is_anomaly']


def test_ensemble_combines_all_base_models(market_data):
    from app.services.anomaly_detector import ENSEMBLE_MEMBERS
    with patch.object(AnomalyDetector, '_fit_score', wraps=AnomalyDetector._fit_score) as spy:
        AnomalyDetector.detect_anomalies(market_data, model_type="ensemble")

    called = [c.args[0] for c in spy.call_args_list]
    assert called[0] == "ensemble"
    assert sorted(called[1:]) == sorted(ENSEMBLE_MEMBERS)


def test_robust_z_puts_models_on_common_scale():
    reference = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    # Skala i przesunięcie wyników modelu nie mają znaczenia po normalizacji
    assert np.allclose(AnomalyDetector._robust_z(reference, reference),
                       AnomalyDetector._robust_z(reference * 100 + 7, reference * 100 + 7))


def test_walk_forward_refit_interval_is_capped_for_long_histories():
    from app.services.anomaly_detector import WALK_FORWARD_MAX_REFITS, WALK_FORWARD_MIN_TRAIN, WALK_FORWARD_REFIT_EVERY
    interval = AnomalyDetector.walk_forward_refit_interval

    assert interval(251) == WALK_FORWARD_REFIT_EVERY
    for n in (500, 1255, 2500):
        assert np.ceil((n - WALK_FORWARD_MIN_TRAIN) / interval(n)) <= WALK_FORWARD_MAX_REFITS


# --- Wyjaśnienia anomalii ---

@pytest.mark.parametrize("mode", ["batch", "walk_forward"])
def test_every_anomaly_has_explanation(market_data, mode):
    from app.services.anomaly_detector import EXPLANATION_TOP_FEATURES
    results = AnomalyDetector.detect_anomalies(market_data, model_type="isolation_forest", mode=mode)

    for r in results:
        if r['is_anomaly']:
            assert 1 <= len(r['explanation']) <= EXPLANATION_TOP_FEATURES
            assert all({'feature', 'value', 'typical', 'z'} <= set(e) for e in r['explanation'])
            # Posortowane od najbardziej odstającej cechy, bez zduplikowanego 'returns'
            zs = [abs(e['z']) for e in r['explanation']]
            assert zs == sorted(zs, reverse=True)
            assert 'returns' not in {e['feature'] for e in r['explanation']}
        else:
            assert r['explanation'] is None


def test_explanation_points_to_injected_volume_spike(market_data):
    from app.services.data_processor import DataProcessor
    spike = 180
    df = pd.DataFrame(market_data)[['date', 'open', 'high', 'low', 'close', 'volume']]
    df['volume'] = df['volume'].astype(float)
    df.loc[spike, 'volume'] *= 8
    data = DataProcessor.add_technical_indicators(df.astype({'open': float, 'high': float, 'low': float, 'close': float}))
    data = data.astype(object).where(pd.notnull(data), None).to_dict(orient='records')

    results = AnomalyDetector.detect_anomalies(data, model_type="lof", contamination=0.05)

    assert results[spike]['is_anomaly']
    assert results[spike]['explanation'][0]['feature'] in {'volume_ratio', 'volume_change'}
    assert results[spike]['explanation'][0]['z'] > 3


def test_explanation_does_not_use_future_data(market_data):
    # Wyjaśnienie sesji t zależy tylko od sesji <= t
    feats = AnomalyDetector.build_features(pd.DataFrame(market_data), impute=False)
    from app.services.anomaly_detector import FEATURES
    feats = feats[FEATURES]
    altered = feats.copy()
    altered.iloc[151:] = altered.iloc[151:] * 5

    assert AnomalyDetector.explain(feats, np.array([150])) == AnomalyDetector.explain(altered, np.array([150]))
