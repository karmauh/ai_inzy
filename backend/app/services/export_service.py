from datetime import datetime

import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace
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
        "title": "Raport analizy StockGuard AI",
        "params_section": "Parametry analizy",
        "symbol": "Symbol", "name": "Nazwa", "sector": "Sektor", "period": "Okres",
        "sessions": ("sesja", "sesje", "sesji"), "model": "Model", "mode": "Tryb detekcji", "sensitivity": "Czułość",
        "sensitivity_note": "sesji oznaczanych jako anomalie", "generated": "Wygenerowano",
        "ai_section": "Ocena modelu językowego",
        "sentiment": "Sentyment", "recommendation": "Rekomendacja", "confidence": "Pewność",
        "ai_disclaimer": "Ocena wygenerowana automatycznie przez model językowy. Nie stanowi rekomendacji inwestycyjnej ani porady inwestycyjnej.",
        "anomalies_section": "Wykryte anomalie",
        "anomalies_total": "Łączna liczba anomalii: {count} z {scored} ocenionych sesji ({share}).",
        "anomalies_latest": "{n} najnowszych anomalii:",
        "anomalies_none": "W analizowanym okresie nie wykryto anomalii.",
        "anomaly_headers": ["Data", "Cena", "Wynik anomalii", "Najbardziej nietypowe cechy"],
        "typical": "typowo",
        "table_section": "Ostatnie notowania",
        "headers": ["Data", "Cena", "RSI", "Anomalia", "Sygnał"],
        "yes": "Tak",
        "disclaimer_title": "Zastrzeżenie",
        "disclaimer": (
            "Wyniki prezentowane w raporcie (wykryte anomalie, wskaźniki techniczne oraz ocena modelu językowego) mają charakter wyłącznie informacyjny i edukacyjny. Nie stanowią rekomendacji inwestycyjnej ani porady inwestycyjnej w rozumieniu przepisów o obrocie instrumentami finansowymi, w szczególności ustawy z dnia 29 lipca 2005 r. o obrocie instrumentami finansowymi oraz rozporządzenia (UE) nr 596/2014 (MAR). Decyzje inwestycyjne podejmujesz samodzielnie i na własne ryzyko."
        ),
        "values": {
            "Bullish": "Wzrostowy", "Bearish": "Spadkowy", "Neutral": "Neutralny",
            "Buy": "Kupuj", "Sell": "Sprzedaj", "Hold": "Trzymaj",
            "High": "Wysoka", "Medium": "Średnia", "Low": "Niska",
        },
        "models": {
            "isolation_forest": "Isolation Forest", "lof": "Local Outlier Factor", "ocsvm": "One-Class SVM",
            "autoencoder": "Autoenkoder (PyTorch)", "ensemble": "Model zespołowy (wszystkie modele)",
        },
        "modes": {"batch": "Analiza historyczna", "walk_forward": "Bez wglądu w przyszłość"},
        # Te same etykiety co w aplikacji (frontend/src/utils/translations.js, sekcja features)
        "features": {
            "return_1d": "Zmiana ceny (1 dzień)", "return_3d": "Zmiana ceny (3 dni)", "return_7d": "Zmiana ceny (7 dni)",
            "momentum_5d": "Momentum (5 dni)", "dist_to_ema20": "Odległość od EMA 20", "drawdown": "Odległość od szczytu",
            "volume_change": "Zmiana wolumenu (d/d)", "volatility_change": "Zmiana zmienności (d/d)",
            "volatility": "Zmienność 20 sesji (% ceny)", "atr": "ATR (% ceny)", "body": "Korpus świecy (% ceny)",
            "upper_shadow": "Górny cień świecy (% ceny)", "lower_shadow": "Dolny cień świecy (% ceny)",
            "volume_ratio": "Wolumen względem średniej z 20 sesji", "rsi": "RSI", "z_score_20": "Odchylenie od SMA 20 (σ)",
            "bb_position": "Pozycja we wstęgach Bollingera",
        },
    },
    "en": {
        "title": "StockGuard AI analysis report",
        "params_section": "Analysis parameters",
        "symbol": "Symbol", "name": "Name", "sector": "Sector", "period": "Period",
        "sessions": ("session", "sessions", "sessions"), "model": "Model", "mode": "Detection mode", "sensitivity": "Sensitivity",
        "sensitivity_note": "of sessions flagged as anomalies", "generated": "Generated",
        "ai_section": "Language model assessment",
        "sentiment": "Sentiment", "recommendation": "Recommendation", "confidence": "Confidence",
        "ai_disclaimer": "Assessment generated automatically by a language model. It is not an investment recommendation or investment advice.",
        "anomalies_section": "Detected anomalies",
        "anomalies_total": "Total number of anomalies: {count} of {scored} scored sessions ({share}).",
        "anomalies_latest": "{n} most recent anomalies:",
        "anomalies_none": "No anomalies were detected in the analyzed period.",
        "anomaly_headers": ["Date", "Close", "Anomaly score", "Most unusual features"],
        "typical": "typically",
        "table_section": "Recent quotes",
        "headers": ["Date", "Close", "RSI", "Anomaly", "Signal"],
        "yes": "Yes",
        "disclaimer_title": "Disclaimer",
        "disclaimer": (
            "The results shown in this report (detected anomalies, technical indicators and the language model assessment) are for informational and educational purposes only. They do not constitute an investment recommendation or investment advice within the meaning of the regulations on trading in financial instruments, in particular the Polish Act of 29 July 2005 on Trading in Financial Instruments and Regulation (EU) No 596/2014 (MAR). You make investment decisions on your own and at your own risk."
        ),
        "values": {},
        "models": {
            "isolation_forest": "Isolation Forest", "lof": "Local Outlier Factor", "ocsvm": "One-Class SVM",
            "autoencoder": "Autoencoder (PyTorch)", "ensemble": "Ensemble (all models)",
        },
        "modes": {"batch": "Historical analysis", "walk_forward": "No look-ahead"},
        "features": {
            "return_1d": "Price change (1 day)", "return_3d": "Price change (3 days)", "return_7d": "Price change (7 days)",
            "momentum_5d": "Momentum (5 days)", "dist_to_ema20": "Distance from EMA 20", "drawdown": "Distance from peak",
            "volume_change": "Volume change (d/d)", "volatility_change": "Volatility change (d/d)",
            "volatility": "20-session volatility (% of price)", "atr": "ATR (% of price)", "body": "Candle body (% of price)",
            "upper_shadow": "Upper shadow (% of price)", "lower_shadow": "Lower shadow (% of price)",
            "volume_ratio": "Volume vs 20-session average", "rsi": "RSI", "z_score_20": "Deviation from SMA 20 (σ)",
            "bb_position": "Position within Bollinger Bands",
        },
    },
}

_RECOMMENDATION_COLORS = {
    "Buy": (34, 139, 34),
    "Sell": (178, 34, 34),
}

REPORT_LATEST_ANOMALIES = 10
REPORT_RECENT_SESSIONS = 15

# Sposób wyświetlania wartości cech – jak formatFeatureValue w frontend/src/utils/explanations.js
_FEATURE_UNITS = {
    'return_1d': 'pctSigned', 'return_3d': 'pctSigned', 'return_7d': 'pctSigned', 'momentum_5d': 'pctSigned',
    'dist_to_ema20': 'pctSigned', 'drawdown': 'pctSigned', 'volume_change': 'pctSigned', 'volatility_change': 'pctSigned',
    'volatility': 'pct', 'atr': 'pct', 'body': 'pct', 'upper_shadow': 'pct', 'lower_shadow': 'pct',
    'volume_ratio': 'ratio', 'rsi': 'number1', 'z_score_20': 'number2', 'bb_position': 'number2',
}


def _format_explanation(explanation: Any) -> str:
    if not isinstance(explanation, list):
        return ''
    return '; '.join(f"{e['feature']}={e['value']:.4g} (z={e['z']:+.1f})" for e in explanation)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value


def _fmt_decimal(value: float, digits: int, language: str) -> str:
    """Liczba z separatorami jak toLocaleString w aplikacji: pl-PL – przecinek i spacja tysięcy od 10 000, en-US – kropka i przecinek."""
    if language == 'en':
        return f"{value:,.{digits}f}"
    text = f"{value:.{digits}f}"
    integer, _, fraction = text.partition('.')
    sign = '-' if integer.startswith('-') else ''
    integer = integer.lstrip('-')
    if len(integer) > 4:
        groups = []
        while integer:
            groups.insert(0, integer[-3:])
            integer = integer[:-3]
        integer = ' '.join(groups)
    return f"{sign}{integer}{',' + fraction if fraction else ''}"


def _fmt_number(value: Any, digits: int, language: str) -> str:
    return _fmt_decimal(value, digits, language) if _is_number(value) else "—"


def _fmt_feature_value(feature: str, value: float, language: str) -> str:
    unit = _FEATURE_UNITS.get(feature)
    if unit == 'pctSigned':
        return f"{'+' if value > 0 else ''}{_fmt_decimal(value * 100, 1, language)}%"
    if unit == 'pct':
        return f"{_fmt_decimal(value * 100, 2, language)}%"
    if unit == 'ratio':
        return f"{_fmt_decimal(value, 1, language)}×"
    if unit == 'number1':
        return _fmt_decimal(value, 1, language)
    return _fmt_decimal(value, 2, language)


def _describe_explanation(explanation: Any, labels: Dict[str, Any], language: str) -> str:
    """Cechy najbardziej odbiegające od normy w zapisie z aplikacji, np. '▲ Wolumen względem średniej z 20 sesji: 4,0× (typowo 1,0×)'."""
    if not isinstance(explanation, list):
        return "—"
    lines = []
    for item in explanation:
        feature = item.get('feature')
        if not _is_number(item.get('value')) or not _is_number(item.get('typical')):
            continue
        arrow = '▲' if (item.get('z') or 0) >= 0 else '▼'
        lines.append(f"{arrow} {labels['features'].get(feature, feature)}: {_fmt_feature_value(feature, item['value'], language)} "
                     f"({labels['typical']} {_fmt_feature_value(feature, item['typical'], language)})")
    return "\n".join(lines) or "—"


def _sessions(count: int, forms: tuple) -> str:
    """Odmiana liczebnika: 1 sesja, 2–4 sesje (poza 12–14), 5+ sesji; po angielsku 1 session / N sessions."""
    one, few, many = forms
    if count == 1:
        return f"{count} {one}"
    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return f"{count} {few}"
    return f"{count} {many}"


def _date(row: Dict[str, Any]) -> str:
    return str(row.get('date') or '—')[:10]


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
    def generate_pdf(data: List[Dict[str, Any]], assessment: Dict[str, Any], ticker_info: Dict[str, Any], language: str = 'pl',
                     analysis: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Generuje raport PDF (fpdf2, obsługa Unicode) z czterema sekcjami: parametry analizy, ocena modelu
        językowego, wykryte anomalie i ostatnie notowania. Liczby zapisywane są zgodnie z językiem raportu
        (przecinek dziesiętny w wersji polskiej, kropka w angielskiej).
        """
        labels = _LABELS.get(language, _LABELS["pl"])
        language = language if language in _LABELS else "pl"
        analysis = analysis or {}

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

        def section(title: str) -> None:
            pdf.ln(4)
            pdf.set_font(main_font, 'B', 12)
            line(9, title)
            pdf.set_font(main_font, '', 10)

        def table(headers: List[str], rows: List[List[str]], col_widths: tuple, align: tuple, padding: Any = 1.5) -> None:
            pdf.set_font(main_font, '', 9)
            with pdf.table(col_widths=col_widths, text_align=align, line_height=4.5, padding=padding,
                           headings_style=FontFace(emphasis="BOLD"), first_row_as_headings=True) as tbl:
                for values in [headers] + rows:
                    tbl.row([txt(v) for v in values])

        pdf.add_page()
        pdf.set_font(main_font, 'B', 16)
        line(10, labels["title"], align='C')

        # 1. Parametry analizy
        section(labels["params_section"])
        dates = [_date(r) for r in data if r.get('date')]
        period = f"{dates[0]} – {dates[-1]} ({_sessions(len(data), labels['sessions'])})" if dates else "—"
        contamination = analysis.get('contamination')
        params = [
            (labels["symbol"], ticker_info.get('symbol')),
            (labels["name"], ticker_info.get('name')),
            (labels["sector"], ticker_info.get('sector')),
            (labels["period"], period),
            (labels["model"], labels["models"].get(analysis.get('model_type'), analysis.get('model_type'))),
            (labels["mode"], labels["modes"].get(analysis.get('mode'), analysis.get('mode'))),
            (labels["sensitivity"], f"{_fmt_decimal(contamination * 100, 0, language)}% {labels['sensitivity_note']}"
                                    if _is_number(contamination) else None),
            (labels["generated"], datetime.now().strftime('%Y-%m-%d %H:%M')),
        ]
        for name, value in params:
            line(6, f"{name}: {value or '—'}")

        # 2. Ocena modelu językowego
        section(labels["ai_section"])
        recommendation = assessment.get('recommendation')
        pdf.set_text_color(*_RECOMMENDATION_COLORS.get(recommendation, (0, 0, 0)))
        line(6, f"{labels['sentiment']}: {value_label(assessment.get('sentiment'))}")
        line(6, f"{labels['recommendation']}: {value_label(recommendation)}")
        line(6, f"{labels['confidence']}: {value_label(assessment.get('confidence'))}")
        pdf.set_text_color(0, 0, 0)

        pdf.set_font(main_font, 'I', 8)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 5, txt(labels["ai_disclaimer"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font(main_font, '', 10)
        # Usunięcie znaczników Markdown (**pogrubienie**) z podsumowania LLM
        summary = (assessment.get('summary') or '').replace('**', '')
        pdf.multi_cell(0, 6, txt(summary), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # 3. Wykryte anomalie – nagłówek nie może zostać sam na dole strony (60 mm: nagłówek, dwa zdania,
        # wiersz nagłówka tabeli i pierwszy wiersz anomalii)
        if pdf.will_page_break(60):
            pdf.add_page()
        section(labels["anomalies_section"])
        anomalies = [r for r in data if r.get('is_anomaly')]
        # W trybie walk-forward sesje z okresu rozruchu nie są oceniane (anomaly_score = None)
        scored = sum(1 for r in data if _is_number(r.get('anomaly_score'))) or len(data)
        if anomalies:
            share = f"{_fmt_decimal(len(anomalies) / scored * 100, 1, language)}%"
            pdf.multi_cell(0, 6, txt(labels["anomalies_total"].format(count=len(anomalies), scored=scored, share=share)),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            latest = anomalies[-REPORT_LATEST_ANOMALIES:][::-1]
            line(6, labels["anomalies_latest"].format(n=len(latest)))
            pdf.ln(1)
            table(labels["anomaly_headers"],
                  [[_date(r), _fmt_number(r.get('close'), 2, language), _fmt_number(r.get('anomaly_score'), 4, language),
                    _describe_explanation(r.get('explanation'), labels, language)] for r in latest],
                  col_widths=(22, 20, 24, 124), align=("LEFT", "RIGHT", "RIGHT", "LEFT"))
        else:
            line(6, labels["anomalies_none"])

        # 4. Ostatnie notowania – sygnał tylko wtedy, gdy rzeczywiście wystąpił.
        # Tabela nie jest dzielona między strony: nagłówek sekcji (~13 mm) + wiersze po ~6,1 mm (4,5 mm tekstu + odstępy)
        recent = data[-REPORT_RECENT_SESSIONS:]
        if pdf.will_page_break(13 + (len(recent) + 1) * 6.1):
            pdf.add_page()
        section(labels["table_section"])
        table(labels["headers"],
              [[_date(r), _fmt_number(r.get('close'), 2, language), _fmt_number(r.get('rsi'), 2, language),
                labels["yes"] if r.get('is_anomaly') else "—",
                value_label(r.get('signal')) if r.get('signal') in ('Buy', 'Sell') else "—"]
               for r in recent],
              col_widths=(38, 38, 38, 38, 38), align=("LEFT", "RIGHT", "RIGHT", "CENTER", "CENTER"), padding=(0.8, 1.5))

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
