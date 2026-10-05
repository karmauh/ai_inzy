import logging
from fastapi import APIRouter, HTTPException
from app.schemas import EvaluateRequest
from app.services.evaluation_service import EvaluationService
from app.utils.json_utils import sanitize_json
from fastapi.encoders import jsonable_encoder

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/evaluate")
def evaluate_models_endpoint(request: EvaluateRequest):
    """
    Uruchamia ujednoliconą ewaluację i porównanie modeli
    wstrzykując zadaną frakcję syntetycznych anomalii do danych wejściowych.
    """
    try:
        results = EvaluationService.evaluate_models(request.data, fraction=request.fraction, models=request.models, n_runs=request.n_runs, mode=request.mode)
    except (KeyError, ValueError, TypeError) as e:
        logger.exception("Błąd podczas ewaluacji modeli")
        raise HTTPException(status_code=400, detail=f"Nieprawidłowe dane do ewaluacji: {e}")
    return jsonable_encoder(sanitize_json(results))
