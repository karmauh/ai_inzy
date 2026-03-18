from fastapi import APIRouter, HTTPException
from app.services.market_data import MarketDataService

router = APIRouter()

@router.get("/data/{symbol}")
async def get_market_data(symbol: str, period: str = "1y"):
    """
    Pobiera dane historyczne dla wybranego symbolu.
    """
    # Pobieranie danych historycznych
    data = MarketDataService.get_historical_data(symbol, period)
    if not data:
        raise HTTPException(status_code=404, detail="Data not found for symbol")
    
    # Pobieranie informacji o aktywie
    info = MarketDataService.get_asset_info(symbol)
    
    return {
        "symbol": symbol,
        "info": info,
        "data": data
    }
