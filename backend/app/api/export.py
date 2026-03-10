from fastapi import APIRouter, Response, Body
from typing import List, Dict, Any
from app.services.export_service import ExportService
import io

router = APIRouter()

@router.post("/csv")
async def export_csv(data: List[Dict[str, Any]] = Body(...)):
    """
    Eksportuje wyniki analizy do pliku CSV.
    """
    csv_content = ExportService.generate_csv(data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=stock_analysis.csv"}
    )

@router.post("/pdf")
async def export_pdf(request_data: Dict[str, Any] = Body(...)):
    """
    Eksportuje kompleksowy raport do pliku PDF.
    """
    data = request_data.get('data', [])
    assessment = request_data.get('assessment', {})
    ticker_info = request_data.get('ticker_info', {})
    language = request_data.get('language', 'pl')
    
    pdf_content = ExportService.generate_pdf(data, assessment, ticker_info, language)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=market_report_{language}.pdf"}
    )
