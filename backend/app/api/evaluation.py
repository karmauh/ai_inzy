from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.evaluation_service import EvaluationService
from fastapi.encoders import jsonable_encoder
import numpy as np

router = APIRouter()

@router.post("/evaluate")
async def evaluate_models_endpoint(request: Dict[str, Any]):
    """
    Uruchamia ujednoliconą ewaluację i porównanie modeli
    wstrzykując zadaną frakcję syntetycznych anomalii do danych wejściowych.
    """
    data_dicts = request.get('data')
    if not data_dicts:
        raise HTTPException(status_code=400, detail="Brak danych do wykonania ewaluacji (klucz 'data').")
        
    fraction = request.get('fraction', 0.05)
    models = request.get('models', ['isolation_forest', 'lof', 'ocsvm', 'autoencoder'])
    
    try:
        results = EvaluationService.evaluate_models(data_dicts, fraction=fraction, models=models)
        
        # Rekurencyjna sanityzacja by uniknąć problemów NaN/Inf w JSON
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
            
        return jsonable_encoder(sanitize(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas ewaluacji modeli: {str(e)}")
