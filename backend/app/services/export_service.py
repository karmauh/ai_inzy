import pandas as pd
from fpdf import FPDF
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


class ExportService:
    @staticmethod
    def generate_csv(data: List[Dict[str, Any]]) -> str:
        """
        Generuje dane CSV z listy wyników analizy.
        """
        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    @staticmethod
    def generate_pdf(data: List[Dict[str, Any]], assessment: Dict[str, Any], ticker_info: Dict[str, Any], language: str = 'pl') -> bytes:
        """
        Generuje raport PDF z wynikami analizy przy użyciu fpdf2 (obsługa Unicode).
        Automatycznie wykrywa dostępne czcionki Unicode na Linuxie i macOS.
        """
        pdf = FPDF()

        # Wykrycie dostępnej czcionki Unicode
        font_regular_path = _find_font(_FONT_CANDIDATES["regular"])
        font_bold_path    = _find_font(_FONT_CANDIDATES["bold"])
        font_italic_path  = _find_font(_FONT_CANDIDATES["italic"])

        unicode_available = font_regular_path is not None
        main_font = 'UniFont' if unicode_available else 'Helvetica'

        if unicode_available:
            pdf.add_font(main_font, '',  font_regular_path, uni=True)
            pdf.add_font(main_font, 'B', font_bold_path   or font_regular_path, uni=True)
            pdf.add_font(main_font, 'I', font_italic_path or font_regular_path, uni=True)

        # Pomocnik: jeśli brak czcionki Unicode, oczyść tekst przed wpisaniem do PDF
        def txt(text: str) -> str:
            return text if unicode_available else _safe_text(text)

        pdf.add_page()
        pdf.set_font(main_font, 'B', 16)

        title = "Raport Analizy StockGuard AI" if language == 'pl' else "StockGuard AI Analysis Report"
        pdf.cell(0, 10, txt(title), ln=True, align='C')
        pdf.ln(5)

        # Sekcja: Informacje o aktywie
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 10, txt("Informacje o Aktywie" if language == 'pl' else "Asset Information"), ln=True)
        pdf.set_font(main_font, '', 10)

        symbol = ticker_info.get('symbol', 'N/A')
        name   = ticker_info.get('name',   'N/A')
        sector = ticker_info.get('sector', 'N/A')

        pdf.cell(0, 8, txt(f"Symbol: {symbol}"), ln=True)
        pdf.cell(0, 8, txt(f"Nazwa: {name}"   if language == 'pl' else f"Name: {name}"),     ln=True)
        pdf.cell(0, 8, txt(f"Sektor: {sector}" if language == 'pl' else f"Sector: {sector}"), ln=True)
        pdf.ln(5)

        # Sekcja: Ocena AI
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 10, txt("Ocena Rynku AI" if language == 'pl' else "AI Market Assessment"), ln=True)
        pdf.set_font(main_font, '', 10)

        sentiment      = assessment.get('sentiment',      'N/A')
        recommendation = assessment.get('recommendation', 'N/A')

        # Kolor rekomendacji
        if any(word in recommendation for word in ["Kupuj", "Buy", "Strong Buy"]):
            pdf.set_text_color(34, 139, 34)
        elif any(word in recommendation for word in ["Sprzedaj", "Sell", "Strong Sell"]):
            pdf.set_text_color(178, 34, 34)
        else:
            pdf.set_text_color(0, 0, 0)

        pdf.cell(0, 8, txt(f"Sentyment: {sentiment}"         if language == 'pl' else f"Sentiment: {sentiment}"),         ln=True)
        pdf.cell(0, 8, txt(f"Rekomendacja: {recommendation}" if language == 'pl' else f"Recommendation: {recommendation}"), ln=True)
        pdf.set_text_color(0, 0, 0)

        pdf.set_font(main_font, 'I', 10)
        summary = assessment.get('summary', '')
        pdf.multi_cell(0, 8, txt(summary))
        pdf.ln(5)

        # Sekcja: Ostatnie notowania (tabela)
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 10, txt("Ostatnie Notowania i Sygnały" if language == 'pl' else "Recent Data & Signals"), ln=True)
        pdf.set_font(main_font, 'B', 9)

        col_width = 45
        headers = ["Data", "Cena", "RSI", txt("Sygnał")] if language == 'pl' else ["Date", "Close", "RSI", "Signal"]
        for header in headers:
            pdf.cell(col_width, 10, header, border=1)
        pdf.ln()

        # Wiersze tabeli (ostatnie 15 sesji)
        pdf.set_font(main_font, '', 9)
        for row in data[-15:]:
            rsi_val   = row.get('rsi',   0)
            close_val = row.get('close', 0)
            pdf.cell(col_width, 8, str(row.get('date', 'N/A')),                                       border=1)
            pdf.cell(col_width, 8, f"{close_val:.2f}" if isinstance(close_val, (int, float)) else str(close_val), border=1)
            pdf.cell(col_width, 8, f"{rsi_val:.2f}"   if isinstance(rsi_val,   (int, float)) else str(rsi_val),   border=1)
            pdf.cell(col_width, 8, txt(str(row.get('signal', 'Hold'))),                               border=1)
            pdf.ln()

        return bytes(pdf.output())
