from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.evaluation_service import EvaluationService
from app.utils.json_utils import sanitize_json
from fastapi.encoders import jsonable_encoder

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
        return jsonable_encoder(sanitize_json(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas ewaluacji modeli: {str(e)}")
