from app.services.llm_service import LLMService
from app.services.anomaly_detector import AnomalyDetector
from app.utils.json_utils import sanitize_json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post("/analyze")
async def analyze_data(request: Dict[str, Any]):
    """
    Analizuje dane pod kątem anomalii i generuje ocenę AI.
    """
    model_type = request.get('model_type', 'isolation_forest')

    if model_type in ["isolation_forest", "lof", "ocsvm", "autoencoder"]:
        data_dicts = request.get('data')
        contamination = request.get('contamination', 0.05)

        results = AnomalyDetector.detect_anomalies(data_dicts, model_type, contamination)

        ticker_info = request.get('ticker_info')
        language = request.get('language', 'pl')
        assessment = LLMService.generate_assessment(data_dicts, results, ticker_info, language)

        response_data = {
            "results": results,
            "assessment": assessment
        }

        return jsonable_encoder(sanitize_json(response_data))
    else:
        raise HTTPException(status_code=400, detail=f"Model {model_type} not supported.")
