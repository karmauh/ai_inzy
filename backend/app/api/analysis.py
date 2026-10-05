from app.services.llm_service import LLMService
from app.services.anomaly_detector import AnomalyDetector
from app.schemas import AnalyzeRequest, AssessmentRequest
from app.utils.json_utils import sanitize_json
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

router = APIRouter()


@router.post("/analyze")
def analyze_data(request: AnalyzeRequest):
    """
    Analizuje dane pod kątem anomalii i generuje ocenę AI.
    """
    try:
        results = AnomalyDetector.detect_anomalies(request.data, request.model_type, request.contamination, request.mode)
    except ValueError as e:
        # Np. za mało danych dla trybu walk-forward
        raise HTTPException(status_code=400, detail=str(e))
    assessment = LLMService.generate_assessment(results, request.ticker_info, request.language)

    return jsonable_encoder(sanitize_json({
        "results": results,
        "assessment": assessment
    }))


@router.post("/assessment")
def generate_assessment(request: AssessmentRequest):
    """
    Generuje samą ocenę AI dla gotowych wyników analizy (np. po zmianie języka – bez ponownego uruchamiania modelu).
    """
    assessment = LLMService.generate_assessment(request.results, request.ticker_info, request.language)
    return jsonable_encoder(sanitize_json(assessment))
