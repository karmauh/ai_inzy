from fastapi import APIRouter, Response, Body
from typing import List, Dict, Any
from app.schemas import ExportPdfRequest
from app.services.export_service import ExportService

router = APIRouter()


@router.post("/csv")
def export_csv(data: List[Dict[str, Any]] = Body(...)):
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
def export_pdf(request: ExportPdfRequest):
    """
    Eksportuje kompleksowy raport do pliku PDF.
    """
    pdf_content = ExportService.generate_pdf(request.data, request.assessment, request.ticker_info, request.language)

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=market_report_{request.language}.pdf"}
    )
