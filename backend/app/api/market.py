from typing import Literal
from fastapi import APIRouter, HTTPException
from app.services.market_data import MarketDataService, MarketDataError

router = APIRouter()

Period = Literal["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


@router.get("/data/{symbol}")
def get_market_data(symbol: str, period: Period = "1y"):
    """
    Pobiera dane historyczne dla wybranego symbolu.
    """
    try:
        data = MarketDataService.get_historical_data(symbol, period)
    except MarketDataError:
        raise HTTPException(status_code=502, detail="Market data provider unavailable")
    if not data:
        raise HTTPException(status_code=404, detail="Data not found for symbol")

    return {
        "symbol": symbol,
        "info": MarketDataService.get_asset_info(symbol),
        "data": data
    }
