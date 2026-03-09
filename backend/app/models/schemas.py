from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockDataPoint(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    ticker: Optional[str] = None
    returns: Optional[float] = None
    volatility: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    anomaly_score: Optional[float] = None
    is_anomaly: Optional[bool] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    atr: Optional[float] = None
    signal: Optional[str] = None # 'Buy' (Kupuj), 'Sell' (Sprzedaj), 'Hold' (Trzymaj)

class AnalysisRequest(BaseModel):
    data: List[StockDataPoint]
    model_type: str = "isolation_forest"
    contamination: float = 0.05
    ticker_info: Optional[Dict[str, Any]] = None
    language: str = "pl"


class ProcessingResponse(BaseModel):
    filename: str
    total_rows: int
    daterange_start: Optional[str]
    daterange_end: Optional[str]
    preview: List[StockDataPoint]
    message: str
