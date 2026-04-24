from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="StockGuard AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dla celów programistycznych
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "StockGuard AI Backend is running"}

from app.api.analysis import router as analysis_router
from app.api.export import router as export_router
from app.api.market import router as market_router
from app.api.evaluation import router as evaluation_router

app.include_router(export_router, prefix="/api/v1/export", tags=["Eksport Danych"])
app.include_router(analysis_router, prefix="/api/v1", tags=["Analiza"])
app.include_router(market_router, prefix="/api/v1/market", tags=["Dane Rynkowe"])
app.include_router(evaluation_router, prefix="/api/v1/evaluation", tags=["Ewaluacja"])
