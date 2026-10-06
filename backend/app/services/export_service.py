import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from typing import List, Dict, Any, Optional
import os

# Ścieżki wyszukiwania czcionek Unicode – od najbardziej preferowanej (Docker/Linux)
# do środowisk deweloperskich (macOS/Windows)
_FONT_SEARCH_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",           # Debian/Ubuntu / Docker
    "/usr/share/fonts/truetype/",                   # Inne dystrybucje Linux
    "/usr/share/fonts/",                            # Ogólna ścieżka Linux
    "/opt/homebrew/share/fonts/",                   # Homebrew macOS (Apple Silicon / Intel)
    os.path.expanduser("~/Library/Fonts/"),         # Czcionki użytkownika macOS
    "/Library/Fonts/",                              # Systemowe czcionki macOS
    "/System/Library/Fonts/Supplemental/",          # Uzupełniające czcionki macOS
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),  # Lokalnie dołączone
]

# Preferowana kolejność kandydatów: DejaVu (Linux/Docker), Arial Unicode (macOS)
_FONT_CANDIDATES = {
    "regular": ["DejaVuSans.ttf",       "Arial Unicode.ttf",  "Arial.ttf"],
    "bold":    ["DejaVuSans-Bold.ttf",  "Arial Bold.ttf",     "Arial.ttf"],
    "italic":  ["DejaVuSans-Oblique.ttf","Arial Italic.ttf",  "Arial.ttf"],
}


def _find_font(filenames: list) -> Optional[str]:
    """Zwraca pierwszą znalezioną ścieżkę do pliku czcionki spośród podanych kandydatów."""
    for filename in filenames:
        for directory in _FONT_SEARCH_DIRS:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
    return None


def _safe_text(text: str) -> str:
    """
    Awaryjne czyszczenie tekstu gdy brak czcionki Unicode:
    zastępuje znaki spoza Latin-1 ich ASCII-odpowiednikami lub '?'.
    """
    return text.encode("latin-1", errors="replace").decode("latin-1")


_LABELS = {
    "pl": {
        "title": "Raport Analizy StockGuard AI",
        "asset_section": "Informacje o Aktywie",
        "name": "Nazwa", "sector": "Sektor",
        "ai_section": "Ocena Rynku AI",
        "sentiment": "Sentyment", "recommendation": "Rekomendacja", "confidence": "Pewność",
        "table_section": "Ostatnie Notowania i Sygnały",
        "headers": ["Data", "Cena", "RSI", "Sygnał"],
        "ai_disclaimer": "Rekomendacja wygenerowana automatycznie przez model AI – nie stanowi rekomendacji inwestycyjnej ani porady inwestycyjnej.",
        "disclaimer_title": "Zastrzeżenie",
        "disclaimer": (
            "Wyniki prezentowane w raporcie (wykryte anomalie, wskaźniki techniczne oraz ocena i sugestie AI) mają charakter wyłącznie informacyjny i edukacyjny. Nie stanowią rekomendacji inwestycyjnej ani porady inwestycyjnej w rozumieniu przepisów o obrocie instrumentami finansowymi, w szczególności ustawy z dnia 29 lipca 2005 r. o obrocie instrumentami finansowymi oraz rozporządzenia (UE) nr 596/2014 (MAR). Decyzje inwestycyjne podejmujesz samodzielnie i na własne ryzyko."
        ),
        "values": {
            "Bullish": "Byczy", "Bearish": "Niedźwiedzi", "Neutral": "Neutralny",
            "Buy": "Kupuj", "Sell": "Sprzedaj", "Hold": "Trzymaj",
            "High": "Wysoka", "Medium": "Średnia", "Low": "Niska",
        },
    },
    "en": {
        "title": "StockGuard AI Analysis Report",
        "asset_section": "Asset Information",
        "name": "Name", "sector": "Sector",
        "ai_section": "AI Market Assessment",
        "sentiment": "Sentiment", "recommendation": "Recommendation", "confidence": "Confidence",
        "table_section": "Recent Data & Signals",
        "headers": ["Date", "Close", "RSI", "Signal"],
        "ai_disclaimer": "Recommendation generated automatically by an AI model – it is not an investment recommendation or investment advice.",
        "disclaimer_title": "Disclaimer",
        "disclaimer": (
            "The results shown in this report (detected anomalies, technical indicators and the AI assessment and suggestions) are for informational and educational purposes only. They do not constitute an investment recommendation or investment advice within the meaning of the regulations on trading in financial instruments, in particular the Polish Act of 29 July 2005 on Trading in Financial Instruments and Regulation (EU) No 596/2014 (MAR). You make investment decisions on your own and at your own risk."
        ),
        "values": {},
    },
}

_RECOMMENDATION_COLORS = {
    "Buy": (34, 139, 34),
    "Sell": (178, 34, 34),
}


def _format_explanation(explanation: Any) -> str:
    if not isinstance(explanation, list):
        return ''
    return '; '.join(f"{e['feature']}={e['value']:.4g} (z={e['z']:+.1f})" for e in explanation)


def _fmt_number(value: Any) -> str:
    return f"{value:.2f}" if isinstance(value, (int, float)) and not isinstance(value, bool) else "N/A"


class ExportService:
    @staticmethod
    def generate_csv(data: List[Dict[str, Any]]) -> str:
        """
        Generuje dane CSV z listy wyników analizy.
        """
        df = pd.DataFrame(data)
        if 'explanation' in df.columns:
            # Lista cech odstających -> czytelny tekst, np. "volume_ratio=4.02 (z=+8.7); return_1d=-0.0999 (z=-6.2)"
            df['explanation'] = df['explanation'].map(_format_explanation)
        return df.to_csv(index=False)

    @staticmethod
    def generate_pdf(data: List[Dict[str, Any]], assessment: Dict[str, Any], ticker_info: Dict[str, Any], language: str = 'pl') -> bytes:
        """
        Generuje raport PDF z wynikami analizy przy użyciu fpdf2 (obsługa Unicode).
        Automatycznie wykrywa dostępne czcionki Unicode na Linuxie i macOS.
        """
        labels = _LABELS.get(language, _LABELS["pl"])

        def value_label(value: Any) -> str:
            value = value or "N/A"
            return labels["values"].get(value, str(value))

        pdf = FPDF()

        # Wykrycie dostępnej czcionki Unicode
        font_regular_path = _find_font(_FONT_CANDIDATES["regular"])
        font_bold_path    = _find_font(_FONT_CANDIDATES["bold"])
        font_italic_path  = _find_font(_FONT_CANDIDATES["italic"])

        unicode_available = font_regular_path is not None
        main_font = 'UniFont' if unicode_available else 'Helvetica'

        if unicode_available:
            pdf.add_font(main_font, '',  font_regular_path)
            pdf.add_font(main_font, 'B', font_bold_path   or font_regular_path)
            pdf.add_font(main_font, 'I', font_italic_path or font_regular_path)

        # Pomocnik: jeśli brak czcionki Unicode, oczyść tekst przed wpisaniem do PDF
        def txt(text: str) -> str:
            return text if unicode_available else _safe_text(text)

        def line(height: float, text: str, **kwargs) -> None:
            pdf.cell(0, height, txt(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT, **kwargs)

        pdf.add_page()
        pdf.set_font(main_font, 'B', 16)
        line(10, labels["title"], align='C')
        pdf.ln(5)

        # Sekcja: Informacje o aktywie
        pdf.set_font(main_font, 'B', 12)
        line(10, labels["asset_section"])
        pdf.set_font(main_font, '', 10)
        line(8, f"Symbol: {ticker_info.get('symbol') or 'N/A'}")
        line(8, f"{labels['name']}: {ticker_info.get('name') or 'N/A'}")
        line(8, f"{labels['sector']}: {ticker_info.get('sector') or 'N/A'}")
        pdf.ln(5)

        # Sekcja: Ocena AI
        pdf.set_font(main_font, 'B', 12)
        line(10, labels["ai_section"])
        pdf.set_font(main_font, '', 10)

        recommendation = assessment.get('recommendation')
        pdf.set_text_color(*_RECOMMENDATION_COLORS.get(recommendation, (0, 0, 0)))
        line(8, f"{labels['sentiment']}: {value_label(assessment.get('sentiment'))}")
        line(8, f"{labels['recommendation']}: {value_label(recommendation)}")
        line(8, f"{labels['confidence']}: {value_label(assessment.get('confidence'))}")
        pdf.set_text_color(0, 0, 0)

        pdf.set_font(main_font, 'I', 8)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 5, txt(labels["ai_disclaimer"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font(main_font, 'I', 10)
        # Usunięcie znaczników Markdown (**pogrubienie**) z podsumowania LLM
        summary = (assessment.get('summary') or '').replace('**', '')
        pdf.multi_cell(0, 8, txt(summary))
        pdf.ln(5)

        # Sekcja: Ostatnie notowania (tabela)
        pdf.set_font(main_font, 'B', 12)
        line(10, labels["table_section"])
        pdf.set_font(main_font, 'B', 9)

        col_width = 45
        for header in labels["headers"]:
            pdf.cell(col_width, 10, txt(header), border=1)
        pdf.ln()

        # Wiersze tabeli (ostatnie 15 sesji)
        pdf.set_font(main_font, '', 9)
        for row in data[-15:]:
            pdf.cell(col_width, 8, txt(str(row.get('date') or 'N/A')), border=1)
            pdf.cell(col_width, 8, _fmt_number(row.get('close')), border=1)
            pdf.cell(col_width, 8, _fmt_number(row.get('rsi')), border=1)
            pdf.cell(col_width, 8, txt(value_label(row.get('signal') or 'Hold')), border=1)
            pdf.ln()

        # Zastrzeżenie prawne na końcu raportu – w całości na jednej stronie
        disclaimer = txt(labels["disclaimer"])
        pdf.set_font(main_font, '', 8)
        disclaimer_lines = len(pdf.multi_cell(0, 4.5, disclaimer, dry_run=True, output="LINES"))
        if pdf.will_page_break(8 + 6 + disclaimer_lines * 4.5):
            pdf.add_page()
        else:
            pdf.ln(8)
        pdf.set_text_color(90, 90, 90)
        pdf.set_font(main_font, 'B', 9)
        line(6, labels["disclaimer_title"])
        pdf.set_font(main_font, '', 8)
        pdf.multi_cell(0, 4.5, disclaimer)
        pdf.set_text_color(0, 0, 0)

        return bytes(pdf.output())
