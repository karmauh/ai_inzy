from app.services.llm_service import LLMService
from typing import Dict, Any
import numpy as np
from app.services.anomaly_detector import AnomalyDetector
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post("/analyze")
async def analyze_data(request: Dict[str, Any]):
    """
    Analizuje dane pod kątem anomalii i generuje ocenę AI.
    """
    model_type = request.get('model_type', 'isolation_forest')
    
    if model_type == "isolation_forest":
        # Dane wejściowe w formacie listy słowników
        data_dicts = request.get('data')
        contamination = request.get('contamination', 0.05)
        
        # Wykrywanie anomalii
        results = AnomalyDetector.detect_isolation_forest(data_dicts, contamination)
        
        # Generowanie interpretacji AI
        ticker_info = request.get('ticker_info')
        language = request.get('language', 'pl')
        assessment = LLMService.generate_assessment(data_dicts, results, ticker_info, language)
        
        response_data = {
            "results": results,
            "assessment": assessment
        }
        
        # Rekurencyjna sanityzacja danych (usuwanie NaN/Inf dla koderów JSON)
        def sanitize(obj):
            if isinstance(obj, float):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return obj
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(v) for v in obj]
            return obj
            
        return jsonable_encoder(sanitize(response_data))
    else:
        raise HTTPException(status_code=400, detail=f"Model {model_type} not supported.")
