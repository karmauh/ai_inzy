import numpy as np
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
import requests

from app.services.data_processor import DataProcessor
from app.services.evaluation_service import EvaluationService
from app.services.export_service import ExportService
from app.services.llm_service import LLMService


# --- DataProcessor ---

def test_rsi_bounds_and_warmup(market_data):
    rsi = pd.Series([r['rsi'] for r in market_data], dtype=float)

    assert rsi.iloc[:14].isna().all()
    assert rsi.iloc[14:].between(0, 100).all()


def test_rsi_is_100_for_monotonic_rise():
    df = pd.DataFrame({'close': range(1, 40), 'high': range(2, 41), 'low': range(0, 39), 'open': range(1, 40)})
    df = DataProcessor.add_technical_indicators(df.astype(float))

    assert df['rsi'].iloc[-1] == pytest.approx(100.0)


# --- EvaluationService ---

def test_injection_is_reproducible_and_recomputes_indicators(market_data):
    first = EvaluationService.inject_synthetic_anomalies(market_data, fraction=0.05)
    second = EvaluationService.inject_synthetic_anomalies(market_data, fraction=0.05)

    injected = [i for i, r in enumerate(first) if r['ground_truth']]
    assert injected == [i for i, r in enumerate(second) if r['ground_truth']]
    assert len(injected) == int(np.ceil(len(market_data) * 0.05))

    # Wskaźniki muszą zostać przeliczone po modyfikacji ceny
    changed = [i for i in injected if first[i]['close'] != market_data[i]['close']]
    if changed and changed[-1] + 1 < len(first):
        i = changed[-1] + 1
        assert first[i]['sma_20'] != market_data[i]['sma_20']


def test_evaluate_models_uses_fraction_as_contamination(market_data):
    with patch('app.services.evaluation_service.AnomalyDetector.detect_anomalies',
               side_effect=lambda data, **kwargs: [{'is_anomaly': False, 'anomaly_score': 0.0} for _ in data]) as mock_detect:
        EvaluationService.evaluate_models(market_data, fraction=0.1, models=['lof'])

    assert mock_detect.call_args.kwargs['contamination'] == 0.1


def test_evaluate_models_returns_mean_and_std_over_runs(market_data):
    result = EvaluationService.evaluate_models(market_data, fraction=0.05, models=['isolation_forest'], n_runs=4)
    model_result = result['evaluation']['isolation_forest']

    assert result['metadata']['n_runs'] == 4
    assert set(model_result['metrics']) == {'precision', 'recall', 'f1_score'}
    assert set(model_result['metrics_std']) == {'precision', 'recall', 'f1_score'}
    assert all(0 <= v <= 1 for v in model_result['metrics_std'].values())
    assert model_result['summary']['total_ground_truth'] == int(np.ceil(len(market_data) * 0.05))
    # Tyle samo anomalii wstrzykniętych co oznaczonych – precision i recall są sobie równe
    assert model_result['summary']['total_anomalies_detect'] == model_result['summary']['total_ground_truth']


def test_evaluate_models_runs_each_seed_once_per_model(market_data):
    with patch('app.services.evaluation_service.AnomalyDetector.detect_anomalies',
               side_effect=lambda data, **kwargs: [{'is_anomaly': False, 'anomaly_score': 0.0} for _ in data]) as mock_detect:
        EvaluationService.evaluate_models(market_data, fraction=0.05, models=['lof', 'ocsvm'], n_runs=3)

    assert mock_detect.call_count == 6


# --- ExportService ---

def test_csv_export(market_data):
    csv = ExportService.generate_csv(market_data[:3])

    assert csv.splitlines()[0].startswith('date,open,high,low,close,volume')
    assert len(csv.splitlines()) == 4


@pytest.mark.parametrize("language", ["pl", "en"])
def test_pdf_export_handles_missing_values(market_data, language):
    pdf = ExportService.generate_pdf(
        market_data,
        {"sentiment": "Bullish", "recommendation": "Buy", "summary": "**RSI** wysoki – zażółć gęślą jaźń", "confidence": None},
        {"symbol": "TEST", "name": None},
        language,
    )

    assert pdf.startswith(b'%PDF')


# --- LLMService ---

def test_parse_response_normalizes_polish_values():
    text = 'Akapit pierwszy.\n\nRekomendacja: Kupuj\n```json\n{"sentiment": "Byczy", "recommendation": "Kupuj", "confidence": "Wysoka"}\n```'
    result = LLMService.parse_response(text)

    assert result == {
        "sentiment": "Bullish",
        "recommendation": "Buy",
        "summary": "Akapit pierwszy.\n\nRekomendacja: Kupuj",
        "confidence": "High",
    }


def test_parse_response_fallback_reads_recommendation_line():
    # Brak bloku JSON; słowo "Buy" w treści nie może przesądzać o rekomendacji
    text = "Sygnał **Buy** z RSI jest słaby.\n\n**Rekomendacja:** Sprzedaj – trend spadkowy."
    result = LLMService.parse_response(text)

    assert result["recommendation"] == "Sell"
    assert result["sentiment"] == "Neutral"


def test_parse_response_unknown_values_fall_back_to_defaults():
    result = LLMService.parse_response('Tekst\n```json\n{"sentiment": null, "recommendation": "Strong Buy!"}\n```')

    assert result["sentiment"] == "Neutral"
    assert result["recommendation"] == "Hold"
    assert result["confidence"] == "Medium"


def test_generate_assessment_without_key_is_localized(monkeypatch, market_data):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    assert "API key" in LLMService.generate_assessment(market_data, None, 'en')['summary']
    assert "klucza API" in LLMService.generate_assessment(market_data, None, 'pl')['summary']


def test_generate_assessment_network_error_uses_timeout_and_hides_details(monkeypatch, market_data):
    monkeypatch.setenv("GEMINI_API_KEY", "secret-key")
    with patch('app.services.llm_service.requests.post', side_effect=requests.Timeout("secret-key leaked?")) as mock_post:
        result = LLMService.generate_assessment(market_data, {"symbol": "TEST"}, 'pl')

    assert mock_post.call_args.kwargs['timeout'] > 0
    assert "secret-key" not in result['summary']
    assert result['recommendation'] == 'Hold'


def test_generate_assessment_success(monkeypatch, market_data):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    response = MagicMock()
    response.json.return_value = {"candidates": [{"content": {"parts": [{"text": 'Opis\n```json\n{"sentiment": "Bearish", "recommendation": "Sell", "confidence": "Low"}\n```'}]}}]}
    with patch('app.services.llm_service.requests.post', return_value=response):
        result = LLMService.generate_assessment(market_data, None, 'en')

    assert result == {"sentiment": "Bearish", "recommendation": "Sell", "summary": "Opis", "confidence": "Low"}


def _ok_response(text='Opis\n```json\n{"recommendation": "Buy"}\n```'):
    ok = MagicMock(status_code=200)
    ok.json.return_value = {"candidates": [{"content": {"parts": [{"text": text}]}}]}
    return ok


def test_generate_assessment_falls_back_to_next_model_on_overload(monkeypatch, market_data):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "primary-model, backup-model")

    with patch('app.services.llm_service.requests.post',
               side_effect=[MagicMock(status_code=503), _ok_response()]) as mock_post:
        result = LLMService.generate_assessment(market_data, None, 'pl')

    urls = [c.args[0] for c in mock_post.call_args_list]
    assert "primary-model" in urls[0] and "backup-model" in urls[1]
    assert result["recommendation"] == "Buy"


def test_generate_assessment_falls_back_on_timeout(monkeypatch, market_data):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "a,b")

    with patch('app.services.llm_service.requests.post', side_effect=[requests.Timeout(), _ok_response()]):
        result = LLMService.generate_assessment(market_data, None, 'en')

    assert result["recommendation"] == "Buy"


def test_generate_assessment_stops_on_non_transient_error(monkeypatch, market_data):
    monkeypatch.setenv("GEMINI_API_KEY", "bad-key")
    monkeypatch.setenv("GEMINI_MODELS", "a,b")
    unauthorized = MagicMock(status_code=403)
    unauthorized.raise_for_status.side_effect = requests.HTTPError("403")

    with patch('app.services.llm_service.requests.post', return_value=unauthorized) as mock_post:
        result = LLMService.generate_assessment(market_data, None, 'en')

    assert mock_post.call_count == 1
    assert result["confidence"] == "Low"


def test_default_models_are_used_without_env(monkeypatch):
    from app.services.llm_service import _gemini_models
    monkeypatch.delenv("GEMINI_MODELS", raising=False)

    assert _gemini_models()[0] == "gemini-3.5-flash-lite"


def test_walk_forward_evaluation_injects_only_into_scored_sessions(market_data, monkeypatch):
    from app.services.anomaly_detector import WALK_FORWARD_MIN_TRAIN
    monkeypatch.setenv("EVALUATION_WORKERS", "1")
    result = EvaluationService.evaluate_models(market_data, fraction=0.05, models=['lof'], n_runs=2, mode='walk_forward')

    scored = len(market_data) - WALK_FORWARD_MIN_TRAIN
    assert result['metadata']['scored_records'] == scored
    assert result['evaluation']['lof']['summary']['total_ground_truth'] == int(np.ceil(scored * 0.05))


def test_walk_forward_evaluation_parallel_matches_sequential(market_data, monkeypatch):
    from app.services import evaluation_service
    kwargs = dict(fraction=0.05, models=['isolation_forest', 'autoencoder'], n_runs=2, mode='walk_forward')

    monkeypatch.setenv("EVALUATION_WORKERS", "1")
    sequential = EvaluationService.evaluate_models(market_data, **kwargs)
    monkeypatch.setenv("EVALUATION_WORKERS", "2")
    try:
        parallel = EvaluationService.evaluate_models(market_data, **kwargs)
    finally:
        evaluation_service.shutdown_pool()

    assert parallel == sequential


def test_walk_forward_evaluation_rejects_too_little_data(market_data):
    with pytest.raises(ValueError, match="Walk-forward"):
        EvaluationService.evaluate_models(market_data[:40], mode='walk_forward')


# --- Scenariusz rozszerzony ---

@pytest.mark.parametrize("seed", range(5))
def test_extended_scenario_respects_budget_and_event_shapes(market_data, seed):
    from app.services.evaluation_service import COLLECTIVE_LENGTH, COLLECTIVE_TYPES, POINT_TYPES
    rows = EvaluationService.inject_synthetic_anomalies(market_data, fraction=0.05, seed=seed, scenario='extended')

    assert sum(r['ground_truth'] for r in rows) == int(np.ceil(len(rows) * 0.05))

    events = {}
    for i, r in enumerate(rows):
        if r['ground_truth']:
            events.setdefault(r['anomaly_event'], []).append((i, r['anomaly_type']))
    for sessions in events.values():
        indices, types = zip(*sessions)
        assert len(set(types)) == 1
        expected_len = COLLECTIVE_LENGTH if types[0] in COLLECTIVE_TYPES else 1
        assert types[0] in POINT_TYPES + COLLECTIVE_TYPES
        assert list(indices) == list(range(indices[0], indices[0] + expected_len))

    # Zdarzenia nie stykają się ze sobą (co najmniej jedna sesja odstępu)
    starts_ends = sorted((min(i for i, _ in s), max(i for i, _ in s)) for s in events.values())
    assert all(nxt[0] - prev[1] >= 2 for prev, nxt in zip(starts_ends, starts_ends[1:]))


def test_extended_drift_shifts_level_without_artificial_reversal(market_data):
    # Po dryfie poziom ceny zostaje przesunięty – brak sztucznego skoku powrotnego po zakończeniu zdarzenia
    for seed in range(20):
        rows = EvaluationService.inject_synthetic_anomalies(market_data, fraction=0.05, seed=seed, scenario='extended')
        drift = [i for i, r in enumerate(rows) if r['anomaly_type'] == 'drift']
        if drift and drift[-1] + 2 < len(rows):
            after = drift[-1] + 1
            original_return = market_data[after + 1]['close'] / market_data[after]['close']
            injected_return = rows[after + 1]['close'] / rows[after]['close']
            assert injected_return == pytest.approx(original_return)
            return
    pytest.fail("Brak zdarzenia typu drift w 20 losowaniach")


def test_basic_scenario_uses_only_point_types(market_data):
    rows = EvaluationService.inject_synthetic_anomalies(market_data, fraction=0.05, seed=1, scenario='basic')

    assert {r['anomaly_type'] for r in rows if r['ground_truth']} <= {'price_spike', 'price_drop', 'volume_spike'}


def test_evaluation_reports_detection_rate_by_type(market_data):
    result = EvaluationService.evaluate_models(market_data, fraction=0.05, models=['lof'], n_runs=3, scenario='extended')
    by_type = result['evaluation']['lof']['by_type']

    assert result['metadata']['scenario'] == 'extended'
    assert by_type and all(0 <= v['detection_rate'] <= 1 and v['events'] > 0 for v in by_type.values())


def test_unknown_scenario_is_rejected(market_data):
    with pytest.raises(ValueError, match="scenario"):
        EvaluationService.inject_synthetic_anomalies(market_data, scenario='nope')
