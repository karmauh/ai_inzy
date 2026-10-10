from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

ModelType = Literal['isolation_forest', 'lof', 'ocsvm', 'autoencoder', 'ensemble']
Language = Literal['pl', 'en']
DetectionMode = Literal['batch', 'walk_forward']
Scenario = Literal['basic', 'extended']

# Minimalna liczba sesji potrzebna, by modele (np. LOF) miały sensowne sąsiedztwo
MIN_DATA_POINTS = 10

DataPoints = List[Dict[str, Any]]


class AnalyzeRequest(BaseModel):
    data: DataPoints = Field(min_length=MIN_DATA_POINTS)
    model_type: ModelType = 'lof'
    contamination: float = Field(default=0.05, gt=0, le=0.5)
    mode: DetectionMode = 'batch'
    ticker_info: Optional[Dict[str, Any]] = None
    language: Language = 'pl'


class AssessmentRequest(BaseModel):
    results: DataPoints = Field(min_length=1)
    ticker_info: Optional[Dict[str, Any]] = None
    language: Language = 'pl'
    # Ustawienia, na których powstały wyniki – opisywane w kontekście dla modelu językowego
    model_type: Optional[ModelType] = None
    mode: Optional[DetectionMode] = None
    contamination: Optional[float] = Field(default=None, gt=0, le=0.5)


class EvaluateRequest(BaseModel):
    data: DataPoints = Field(min_length=MIN_DATA_POINTS)
    fraction: float = Field(default=0.05, gt=0, le=0.5)
    # Liczba powtórzeń ewaluacji z różnymi seedami (wynik: średnia ± odchylenie standardowe)
    n_runs: int = Field(default=10, ge=1, le=30)
    mode: DetectionMode = 'batch'
    # Zestaw wstrzykiwanych anomalii: 'basic' (duże, pojedyncze) lub 'extended' (realistyczne, także wielosesyjne)
    scenario: Scenario = 'basic'
    models: List[ModelType] = Field(
        default_factory=lambda: ['isolation_forest', 'lof', 'ocsvm', 'autoencoder', 'ensemble'],
        min_length=1,
    )


class ExportPdfRequest(BaseModel):
    data: DataPoints = Field(default_factory=list)
    assessment: Dict[str, Any] = Field(default_factory=dict)
    ticker_info: Dict[str, Any] = Field(default_factory=dict)
    language: Language = 'pl'
    model_type: Optional[ModelType] = None
    mode: Optional[DetectionMode] = None
    contamination: Optional[float] = Field(default=None, gt=0, le=0.5)
