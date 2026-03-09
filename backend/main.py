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

from app.api.upload import router as upload_router
from app.api.analysis import router as analysis_router
from app.api.market import router as market_router

app.include_router(upload_router, prefix="/api/v1", tags=["Pobieranie Danych"])
app.include_router(analysis_router, prefix="/api/v1", tags=["Analiza"])
app.include_router(market_router, prefix="/api/v1/market", tags=["Dane Rynkowe"])
```
