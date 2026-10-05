import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.export import router as export_router
from app.api.market import router as market_router
from app.api.evaluation import router as evaluation_router

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="StockGuard AI API")

# Lista dozwolonych originów rozdzielona przecinkami (domyślnie serwer deweloperski Vite)
cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def read_root():
    return {"message": "StockGuard AI Backend is running"}


app.include_router(export_router, prefix="/api/v1/export", tags=["Eksport Danych"])
app.include_router(analysis_router, prefix="/api/v1", tags=["Analiza"])
app.include_router(market_router, prefix="/api/v1/market", tags=["Dane Rynkowe"])
app.include_router(evaluation_router, prefix="/api/v1/evaluation", tags=["Ewaluacja"])
