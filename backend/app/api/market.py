from concurrent.futures import ThreadPoolExecutor
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
    # Notowania i metadane pobierane równolegle (dwa niezależne zapytania do Yahoo)
    with ThreadPoolExecutor(max_workers=1) as executor:
        info_future = executor.submit(MarketDataService.get_asset_info, symbol)
        try:
            data = MarketDataService.get_historical_data(symbol, period)
        except MarketDataError:
            raise HTTPException(status_code=502, detail="Market data provider unavailable")
        if not data:
            raise HTTPException(status_code=404, detail="Data not found for symbol")
        info = info_future.result()

    return {
        "symbol": symbol,
        "info": info,
        "data": data
    }
