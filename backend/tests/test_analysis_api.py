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
    
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]
