from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.data_processor import DataProcessor
from app.models.schemas import ProcessingResponse

router = APIRouter()

@router.post("/upload", response_model=ProcessingResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Umożliwia wgranie pliku CSV z danymi giełdowymi.
    Wymagane kolumny: Date, Open, High, Low, Close, Volume.
    """
    result = await DataProcessor.process_csv_upload(file)
    return result
