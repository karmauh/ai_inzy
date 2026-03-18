import pandas as pd
from fpdf import FPDF
import io
from typing import List, Dict, Any
import os

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
        """
        pdf = FPDF()
        
        # Ścieżki do czcionek
        linux_font_path = "/usr/share/fonts/truetype/dejavu/"
        win_font_path = "C:\\Windows\\Fonts\\"
        
        if os.path.exists(os.path.join(win_font_path, "arial.ttf")):
            font_regular = os.path.join(win_font_path, "arial.ttf")
            font_bold = os.path.join(win_font_path, "arialbd.ttf")
            font_oblique = os.path.join(win_font_path, "ariali.ttf")
            main_font = 'Arial'
        else:
            font_regular = os.path.join(linux_font_path, "DejaVuSans.ttf")
            font_bold = os.path.join(linux_font_path, "DejaVuSans-Bold.ttf")
            font_oblique = os.path.join(linux_font_path, "DejaVuSans-Oblique.ttf")
            main_font = 'DejaVu'

        # Dodanie czcionek Unicode
        if os.path.exists(font_regular):
            pdf.add_font(main_font, '', font_regular, uni=True)
            if os.path.exists(font_bold):
                pdf.add_font(main_font, 'B', font_bold, uni=True)
            else:
                pdf.add_font(main_font, 'B', font_regular, uni=True)
                
            if os.path.exists(font_oblique):
                pdf.add_font(main_font, 'I', font_oblique, uni=True)
            else:
                pdf.add_font(main_font, 'I', font_regular, uni=True)
        else:
            # Fallback do Helvetica (standardowa czcionka PDF)
            main_font = 'Helvetica'

        pdf.add_page()
        pdf.set_font(main_font, 'B', 16)
        
        title = "Raport Analizy StockGuard AI" if language == 'pl' else "StockGuard AI Analysis Report"
        pdf.cell(0, 10, title, ln=True, align='C')
        pdf.ln(5)
        
        # Sekcja: Informacje o spółce
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 10, "Informacje o Aktywie" if language == 'pl' else "Asset Information", ln=True)
        pdf.set_font(main_font, '', 10)
        
        symbol = ticker_info.get('symbol', 'N/A')
        name = ticker_info.get('name', 'N/A')
        sector = ticker_info.get('sector', 'N/A')
        
        pdf.cell(0, 8, f"Symbol: {symbol}", ln=True)
        pdf.cell(0, 8, f"Nazwa: {name}" if language == 'pl' else f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Sektor: {sector}" if language == 'pl' else f"Sector: {sector}", ln=True)
        pdf.ln(5)
        
        # Sekcja: Ocena AI
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 10, "Ocena Rynku AI" if language == 'pl' else "AI Market Assessment", ln=True)
        pdf.set_font(main_font, '', 10)
        
        sentiment = assessment.get('sentiment', 'N/A')
        recommendation = assessment.get('recommendation', 'N/A')
        
        # Ustawienie kolorów dla rekomendacji
        if any(word in recommendation for word in ["Kupuj", "Buy", "Strong Buy"]):
            pdf.set_text_color(34, 139, 34) # Green
        elif any(word in recommendation for word in ["Sprzedaj", "Sell", "Strong Sell"]):
            pdf.set_text_color(178, 34, 34) # Red
        else:
            pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 8, f"Sentyment: {sentiment}" if language == 'pl' else f"Sentiment: {sentiment}", ln=True)
        pdf.cell(0, 8, f"Rekomendacja: {recommendation}" if language == 'pl' else f"Recommendation: {recommendation}", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font(main_font, 'I', 10)
        summary = assessment.get('summary', '')
        # fpdf2 multi_cell obsługuje rozbijanie długiego tekstu
        pdf.multi_cell(0, 8, summary)
        pdf.ln(5)
        
        # Sekcja: Ostatnie wyniki (Tabela)
        pdf.set_font(main_font, 'B', 12)
        pdf.cell(0, 10, "Ostatnie Notowania i Sygnały" if language == 'pl' else "Recent Data & Signals", ln=True)
        pdf.set_font(main_font, 'B', 9)
        
        # Nagłówki tabeli
        col_width = 45
        headers = ["Data", "Cena", "RSI", "Sygnał"] if language == 'pl' else ["Date", "Close", "RSI", "Signal"]
        for header in headers:
            pdf.cell(col_width, 10, header, border=1)
        pdf.ln()
        
        # Wiersze tabeli (ostatnie 15 dni)
        pdf.set_font(main_font, '', 9)
        recent_data = data[-15:]
        for row in recent_data:
            pdf.cell(col_width, 8, str(row.get('date', 'N/A')), border=1)
            pdf.cell(col_width, 8, f"{row.get('close', 0):.2f}", border=1)
            pdf.cell(col_width, 8, f"{row.get('rsi', 0):.2f}", border=1)
            pdf.cell(col_width, 8, str(row.get('signal', 'Hold')), border=1)
            pdf.ln()
            
        # fpdf2: output() zwraca bajty raportu jeśli nie podano nazwy pliku
        return pdf.output(dest='S').encode('latin-1')
