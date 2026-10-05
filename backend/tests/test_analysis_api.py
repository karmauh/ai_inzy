import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def request_payload():
    return {
        "model_type": "isolation_forest",
        "contamination": 0.1,
        "data": [
            {
                'date': f'2026-04-{i:02d}', 
                'open': 100, 
                'high': 105, 
                'low': 95, 
                'close': 100, 
                'volume': 1000, 
                'returns': 0.01, 
                'volatility': 0.02, 
                'rsi': 50, 
                'atr': 5, 
                'bb_upper': 110, 
                'bb_lower': 90,
                'macd': 0.1,
                'macd_signal': 0.05,
                'ema_20': 100.5,
                'ema_50': 100.1,
                'sma_20': 100.0,
                'sma_50': 99.0
            }
            for i in range(1, 15)
        ],
        "ticker_info": {"symbol": "TEST", "name": "Test Company"}
    }

@patch('app.services.llm_service.LLMService.generate_assessment')
def test_analyze_endpoint_success(mock_generate, request_payload):
    # Mockujemy zewnętrzną usługę LLM, aby test był szybki i polegał na danych lokalnych
    mock_generate.return_value = {
        "sentiment": "Neutral",
        "recommendation": "Hold",
        "summary": "Mockowany test podsumowania algorytmu.",
        "confidence": "Medium"
    }
    
    response = client.post("/api/v1/analyze", json=request_payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Test struktury odpowiedzi
    assert "results" in data
    assert "assessment" in data
    
    assert len(data["results"]) == 14
    assert data["assessment"]["summary"] == "Mockowany test podsumowania algorytmu."
    assert "is_anomaly" in data["results"][0]
    assert "anomaly_score" in data["results"][0]

def test_analyze_endpoint_invalid_model(request_payload):
    request_payload["model_type"] = "nieistniejacy_model"
    response = client.post("/api/v1/analyze", json=request_payload)

    assert response.status_code == 422


@pytest.mark.parametrize("contamination", [0, -0.1, 0.7])
def test_analyze_endpoint_invalid_contamination(request_payload, contamination):
    request_payload["contamination"] = contamination
    response = client.post("/api/v1/analyze", json=request_payload)

    assert response.status_code == 422


def test_analyze_endpoint_too_little_data(request_payload):
    request_payload["data"] = request_payload["data"][:3]
    response = client.post("/api/v1/analyze", json=request_payload)

    assert response.status_code == 422


@patch('app.services.llm_service.LLMService.generate_assessment')
def test_assessment_endpoint_does_not_rerun_model(mock_generate, request_payload):
    mock_generate.return_value = {"sentiment": "Bullish", "recommendation": "Buy", "summary": "ok", "confidence": "High"}

    with patch('app.services.anomaly_detector.AnomalyDetector.detect_anomalies') as mock_detect:
        response = client.post("/api/v1/assessment", json={
            "results": request_payload["data"],
            "ticker_info": request_payload["ticker_info"],
            "language": "en"
        })
        mock_detect.assert_not_called()

    assert response.status_code == 200
    assert response.json()["recommendation"] == "Buy"
    assert mock_generate.call_args.args[2] == "en"


@patch('app.services.market_data.MarketDataService.get_historical_data')
def test_market_endpoint_provider_error_returns_502(mock_history):
    from app.services.market_data import MarketDataError
    mock_history.side_effect = MarketDataError("timeout")

    response = client.get("/api/v1/market/data/AAPL")

    assert response.status_code == 502


@patch('app.services.market_data.MarketDataService.get_historical_data', return_value=[])
def test_market_endpoint_unknown_symbol_returns_404(_mock_history):
    response = client.get("/api/v1/market/data/NOPE")

    assert response.status_code == 404


def test_market_endpoint_invalid_period():
    response = client.get("/api/v1/market/data/AAPL?period=abc")

    assert response.status_code == 422


@pytest.mark.parametrize("n_runs", [0, 31])
def test_evaluate_endpoint_validates_n_runs(request_payload, n_runs):
    response = client.post("/api/v1/evaluation/evaluate", json={"data": request_payload["data"], "n_runs": n_runs})

    assert response.status_code == 422
