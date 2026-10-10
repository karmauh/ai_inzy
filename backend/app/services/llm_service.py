from typing import List, Dict, Any, Optional
import os
import json
import logging
import re
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Modele próbowane po kolei – kolejny jest używany, gdy poprzedni jest przeciążony lub niedostępny.
# Domyślnie lekkie modele "flash-lite", które są znacznie mniej oblegane niż "flash".
DEFAULT_GEMINI_MODELS = "gemini-3.5-flash-lite,gemini-3.1-flash-lite"
GEMINI_TIMEOUT_SECONDS = 30
# Przeciążenie, limit zapytań, błąd serwera lub wycofany model – warto spróbować następnego modelu
_FALLBACK_STATUS = {404, 429, 500, 502, 503, 504}


def _gemini_models() -> List[str]:
    models = os.getenv("GEMINI_MODELS", DEFAULT_GEMINI_MODELS)
    return [m.strip() for m in models.split(",") if m.strip()]

# Kanoniczne wartości zwracane przez API (tłumaczone po stronie frontendu i raportu PDF).
# Klucze słowników to warianty, które może zwrócić model (małe litery).
_SENTIMENT_ALIASES = {
    "bullish": "Bullish", "byczy": "Bullish", "wzrostowy": "Bullish",
    "bearish": "Bearish", "niedźwiedzi": "Bearish", "spadkowy": "Bearish",
    "neutral": "Neutral", "neutralny": "Neutral",
}
_RECOMMENDATION_ALIASES = {
    "buy": "Buy", "kupuj": "Buy", "kup": "Buy",
    "sell": "Sell", "sprzedaj": "Sell",
    "hold": "Hold", "trzymaj": "Hold",
}
_CONFIDENCE_ALIASES = {
    "high": "High", "wysoka": "High",
    "medium": "Medium", "średnia": "Medium",
    "low": "Low", "niska": "Low",
}

_MESSAGES = {
    "no_data": {"pl": "Brak danych do analizy.", "en": "No data available."},
    "no_key": {
        "pl": "Brak klucza API (GEMINI_API_KEY) dla modelu LLM w pliku .env.",
        "en": "Missing LLM API key (GEMINI_API_KEY) in the .env file.",
    },
    "unavailable": {
        "pl": "Usługa AI jest chwilowo niedostępna. Spróbuj ponownie później.",
        "en": "The AI service is temporarily unavailable. Please try again later.",
    },
}


# Kontekst dla modelu językowego: okno, w którym liczymy anomalie (porównanie z oczekiwaną liczbą),
# oraz dłuższe okno, z którego opisujemy najnowsze anomalie (by nie pominąć ważnej serii sprzed kilku tygodni)
CONTEXT_ANOMALY_WINDOW = 30
CONTEXT_ANOMALY_LIST_WINDOW = 60
CONTEXT_MAX_ANOMALIES = 5

# Czytelne nazwy cech z wyjaśnień anomalii (AnomalyDetector.explain) i sposób formatowania ich wartości
_FEATURE_LABELS = {
    'return_1d': ('zmiana ceny 1 dzień', 'pct'), 'return_3d': ('zmiana ceny 3 dni', 'pct'),
    'return_7d': ('zmiana ceny 7 dni', 'pct'), 'momentum_5d': ('momentum 5 dni', 'pct'),
    'dist_to_ema20': ('odległość od EMA20', 'pct'), 'drawdown': ('odległość od szczytu', 'pct'),
    'volume_change': ('zmiana wolumenu d/d', 'pct'), 'volatility_change': ('zmiana zmienności d/d', 'pct'),
    'volatility': ('zmienność 20 sesji (% ceny)', 'pct'), 'atr': ('ATR (% ceny)', 'pct'),
    'body': ('korpus świecy (% ceny)', 'pct'), 'upper_shadow': ('górny cień świecy (% ceny)', 'pct'),
    'lower_shadow': ('dolny cień świecy (% ceny)', 'pct'), 'volume_ratio': ('wolumen vs średnia 20 sesji', 'ratio'),
    'rsi': ('RSI', 'num'), 'z_score_20': ('odchylenie od SMA20 w sigmach', 'num'),
    'bb_position': ('pozycja we wstęgach Bollingera (0 = dolna, 1 = górna)', 'num'),
}
_MODEL_NAMES = {
    'isolation_forest': 'Isolation Forest', 'lof': 'Local Outlier Factor', 'ocsvm': 'One-Class SVM',
    'autoencoder': 'Autoencoder', 'ensemble': 'Ensemble (wszystkie modele)',
}
_MODE_NAMES = {
    'batch': 'analiza historyczna (model uczony na całym okresie)',
    'walk_forward': 'bez wglądu w przyszłość (każda sesja oceniana modelem uczonym tylko na wcześniejszych)',
}


def _num(value: Any) -> Optional[float]:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _pct(value: Optional[float], signed: bool = True) -> str:
    if value is None:
        return "brak danych"
    return f"{value * 100:+.1f}%" if signed else f"{value * 100:.1f}%"


def _feature(item: Dict[str, Any]) -> str:
    label, unit = _FEATURE_LABELS.get(item['feature'], (item['feature'], 'num'))
    fmt = {'pct': lambda v: _pct(v), 'ratio': lambda v: f"{v:.1f}x"}.get(unit, lambda v: f"{v:.2f}")
    return f"{label} {fmt(item['value'])} (typowo {fmt(item['typical'])})"


def _change(closes: List[Optional[float]], sessions: int) -> Optional[float]:
    if len(closes) <= sessions or closes[-1] is None or not closes[-1 - sessions]:
        return None
    return closes[-1] / closes[-1 - sessions] - 1


def build_market_context(results: List[Dict[str, Any]], analysis: Optional[Dict[str, Any]] = None) -> str:
    """
    Zwięzły opis sytuacji z całego analizowanego okresu (a nie tylko ostatniej sesji):
    trend, zmienność, wolumen, ostatnie sygnały i ostatnie anomalie wraz z wyjaśnieniami.
    """
    closes = [_num(r.get('close')) for r in results]
    valid = [c for c in closes if c is not None]
    lines = []

    if valid:
        first_date, last_date = results[0].get('date'), results[-1].get('date')
        lines.append(f"Okres analizy: {len(results)} sesji ({first_date} – {last_date}).")
        lines.append("Zmiana ceny: " + ", ".join(
            f"{label} {_pct(_change(closes, n))}" for label, n in
            (("5 sesji", 5), ("20 sesji", 20), ("60 sesji", 60), ("cały okres", len(closes) - 1))
        ) + ".")
        high, low, last = max(valid), min(valid), valid[-1]
        lines.append(f"Cena względem okresu: {_pct(last / high - 1)} od maksimum, {_pct(last / low - 1)} od minimum.")

        returns = [b / a - 1 for a, b in zip(valid, valid[1:]) if a]
        if len(returns) >= 40:
            def stdev(xs):
                mean = sum(xs) / len(xs)
                return (sum((x - mean) ** 2 for x in xs) / len(xs)) ** 0.5
            recent = stdev(returns[-20:])
            typical = sorted(stdev(returns[i - 20:i]) for i in range(20, len(returns) + 1))[len(returns[19:]) // 2]
            lines.append(f"Zmienność dzienna (20 sesji): {_pct(recent, signed=False)}, typowo w tym okresie {_pct(typical, signed=False)}.")

        volumes = [_num(r.get('volume')) for r in results]
        recent_vol = [v for v in volumes[-5:] if v]
        base_vol = [v for v in volumes[-60:] if v]
        if recent_vol and base_vol:
            ratio = (sum(recent_vol) / len(recent_vol)) / (sum(base_vol) / len(base_vol))
            lines.append(f"Średni wolumen 5 ostatnich sesji: {ratio:.1f}x średniej z 60 sesji.")

    signals = [r for r in results if r.get('signal') in ('Buy', 'Sell')]
    if signals:
        last_signal = signals[-1]
        name = 'kupna' if last_signal['signal'] == 'Buy' else 'sprzedaży'
        lines.append(f"Ostatni sygnał techniczny: sygnał {name} ({last_signal.get('date')}; RSI i wstęgi Bollingera).")
    else:
        lines.append("Brak sygnałów kupna/sprzedaży (RSI + wstęgi Bollingera) w ostatnich 60 dniach.")

    if analysis:
        model = _MODEL_NAMES.get(analysis.get('model_type'), analysis.get('model_type'))
        mode = _MODE_NAMES.get(analysis.get('mode'), analysis.get('mode'))
        contamination = _num(analysis.get('contamination'))
        sensitivity = f", czułość {contamination * 100:.0f}% sesji oznaczanych jako anomalie" if contamination else ""
        lines.append(f"Detekcja anomalii: model {model}, tryb: {mode}{sensitivity}.")

    window = results[-CONTEXT_ANOMALY_WINDOW:]
    anomalies = [(i, r) for i, r in enumerate(results) if r.get('is_anomaly')]
    recent = [(i, r) for i, r in anomalies if i >= len(results) - CONTEXT_ANOMALY_WINDOW]
    contamination = _num((analysis or {}).get('contamination'))
    expected = f" (przy tej czułości oczekiwane ok. {contamination * len(window):.1f})" if contamination else ""
    lines.append(f"Anomalie w ostatnich {len(window)} sesjach: {len(recent)}{expected}; w całym okresie: {len(anomalies)}.")
    if anomalies:
        lines.append(f"Ostatnia anomalia: {len(results) - 1 - anomalies[-1][0]} sesji temu.")
    listed = [(i, r) for i, r in anomalies if i >= len(results) - CONTEXT_ANOMALY_LIST_WINDOW][-CONTEXT_MAX_ANOMALIES:]
    if listed:
        lines.append(f"Najnowsze anomalie z ostatnich {CONTEXT_ANOMALY_LIST_WINDOW} sesji (od najnowszej):")
    for i, r in reversed(listed):
        day_change = _change(closes[:i + 1], 1)
        features = "; ".join(_feature(e) for e in (r.get('explanation') or [])[:2])
        lines.append(f"- {r.get('date')}: zmiana ceny {_pct(day_change)}" + (f"; nietypowe: {features}" if features else ""))

    return "\n".join(lines)


def _normalize(value: Any, aliases: Dict[str, str], default: str) -> str:
    if not isinstance(value, str):
        return default
    return aliases.get(value.strip().lower(), default)


def _fallback(message_key: str, language: str) -> Dict[str, Any]:
    return {
        "sentiment": "Neutral",
        "recommendation": "Hold",
        "summary": _MESSAGES[message_key][language],
        "confidence": "Low",
    }


class LLMService:
    @staticmethod
    def build_prompt(results: List[Dict[str, Any]], ticker_info: Optional[Dict[str, Any]], language: str,
                     analysis: Optional[Dict[str, Any]] = None) -> str:
        last_point = results[-1]

        def fmt(val):
            return f"{val:.2f}" if isinstance(val, (int, float)) and not isinstance(val, bool) else "brak danych"

        ticker_str = (
            f"Ticker: {ticker_info.get('symbol', 'N/A')} ({ticker_info.get('name', 'N/A')})"
            if ticker_info else "Ticker: Nieznany"
        )
        lang_instruction = "angielskim" if language == "en" else "polskim"
        recommendation_words = "Buy / Hold / Sell" if language == "en" else "Kupuj / Trzymaj / Sprzedaj"
        decimal_example = "10.7%" if language == "en" else "10,7%"
        is_anomaly = last_point.get('is_anomaly', False)
        context = build_market_context(results, analysis)

        return f"""
Jesteś asystentem-analitykiem rynków finansowych w aplikacji StockGuard AI.
Otrzymujesz przetworzone dane dla jednego instrumentu (akcja, ETF, kryptowaluta lub indeks): wskaźniki techniczne z ostatniej sesji, kontekst z całego analizowanego okresu (trend, zmienność, wolumen, sygnały) oraz anomalie statystyczne wykryte przez model uczenia maszynowego, wraz z opisem, co w danej sesji było nietypowe.
Twoim zadaniem jest:

- Krótko podsumować aktualną sytuację instrumentu, uwzględniając trend z ostatnich tygodni, a nie tylko ostatnią sesję.
- Zinterpretować wskaźniki techniczne (RSI, MACD, wstęgi Bollingera, ATR, EMA) w świetle tego trendu.
- Omówić ostatnie anomalie: co było w nich nietypowe (np. wolumen, gwałtowny ruch ceny) i co może to sugerować. Jeśli anomalii jest więcej niż oczekiwano, zaznacz to; jeśli brak ich w ostatnich sesjach, powiedz to krótko.
- Na końcu sformułować prostą rekomendację wraz z 2–3 zdaniami uzasadnienia.

Zasady:
- Wyróżniaj kluczowe pojęcia znacznikami Markdown `**pogrubienie**`.
- Podziel odpowiedź na 2 do 3 akapitów, nie twórz jednolitej ściany tekstu.
- Zacznij od razu od treści analizy – bez wstępów typu „Oto analiza…” i bez tytułów.
- Używaj prostego języka, ale z poprawną terminologią techniczną.
- Nie podawaj konkretnych cen docelowych ani gwarancji wyniku.
- Liczby dziesiętne zapisuj zgodnie z zasadami języka odpowiedzi (np. {decimal_example}).
- Jeśli dane są sprzeczne lub niejednoznaczne, wyraźnie to zaznacz i wybierz bardziej zachowawczą rekomendację.
- Jeśli brakuje jakiegoś wskaźnika, powiedz „brak danych” zamiast zgadywać.
- Anomalia oznacza nietypowe zachowanie, a nie automatycznie sygnał kupna czy sprzedaży – nie nadinterpretuj jej.
- Odpowiadaj w języku {lang_instruction}, ale nazwy wskaźników (RSI, MACD, itp.) zostaw w oryginale. W treści rekomendację również podaj w języku odpowiedzi ({recommendation_words}).

KONIECZNIE NA SAMYM KOŃCU ODPOWIEDZI DODAJ BLOK JSON. Wartości pól podaj ZAWSZE po angielsku, dokładnie jedną z wymienionych opcji (niezależnie od języka odpowiedzi):
```json
{{
  "sentiment": "Bullish" | "Bearish" | "Neutral",
  "recommendation": "Buy" | "Hold" | "Sell",
  "confidence": "High" | "Medium" | "Low"
}}
```

Dane techniczne rynkowe:
-------------------------
{ticker_str}
Ostatnia cena zamknięcia: {fmt(last_point.get('close'))}
RSI(14): {fmt(last_point.get('rsi'))}
MACD: {fmt(last_point.get('macd'))} (Signal: {fmt(last_point.get('macd_signal'))})
EMA(20): {fmt(last_point.get('ema_20'))}
EMA(50): {fmt(last_point.get('ema_50'))}
ATR(14): {fmt(last_point.get('atr'))}
Wstęgi Bollingera (Górna/Dolna): {fmt(last_point.get('bb_upper'))} / {fmt(last_point.get('bb_lower'))}
Czy wykryto anomalię statystyczną na ostatniej sesji?: {'Tak' if is_anomaly else 'Nie'}
-------------------------

Kontekst z analizowanego okresu:
-------------------------
{context}
-------------------------
"""

    @staticmethod
    def parse_response(text_output: str) -> Dict[str, Any]:
        """
        Rozdziela treść raportu od końcowego bloku JSON i normalizuje pola do wartości kanonicznych.
        """
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text_output, re.DOTALL | re.IGNORECASE)
        parsed: Dict[str, Any] = {}
        summary = text_output.strip()

        if json_match:
            summary = text_output[:json_match.start()].strip()
            try:
                parsed = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                logger.warning("Nie udało się sparsować bloku JSON z odpowiedzi LLM")

        recommendation = parsed.get("recommendation")
        if recommendation is None:
            # Fallback: linia "Rekomendacja: X" / "Recommendation: X" w treści
            rec_match = re.search(r'(?:Rekomendacja|Recommendation)\**\s*:\s*\**\s*([\wąćęłńóśźż]+)', summary, re.IGNORECASE)
            recommendation = rec_match.group(1) if rec_match else None

        return {
            "sentiment": _normalize(parsed.get("sentiment"), _SENTIMENT_ALIASES, "Neutral"),
            "recommendation": _normalize(recommendation, _RECOMMENDATION_ALIASES, "Hold"),
            "summary": summary,
            "confidence": _normalize(parsed.get("confidence"), _CONFIDENCE_ALIASES, "Medium"),
        }

    @staticmethod
    def generate_assessment(results: List[Dict[str, Any]], ticker_info: Optional[Dict[str, Any]] = None, language: str = 'pl',
                            analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generuje ocenę i interpretację wyników analizy używając modelu LLM (Google Gemini).
        Pola sentiment/recommendation/confidence mają wartości kanoniczne (EN), summary jest w wybranym języku.
        """
        language = language if language in ('pl', 'en') else 'pl'
        if not results:
            return _fallback("no_data", language)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return _fallback("no_key", language)

        prompt = LLMService.build_prompt(results, ticker_info, language, analysis)

        for model in _gemini_models():
            try:
                response = requests.post(
                    GEMINI_URL_TEMPLATE.format(model=model),
                    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=GEMINI_TIMEOUT_SECONDS,
                )
            except requests.RequestException:
                logger.warning("Brak odpowiedzi od modelu %s, próbuję kolejnego", model, exc_info=True)
                continue

            if response.status_code in _FALLBACK_STATUS:
                logger.warning("Model %s zwrócił %s, próbuję kolejnego", model, response.status_code)
                continue

            try:
                response.raise_for_status()
                text_output = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                return LLMService.parse_response(text_output)
            except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
                # Błąd nieprzejściowy (np. zły klucz API, zablokowana odpowiedź) – kolejny model nie pomoże
                logger.exception("Błąd odpowiedzi modelu %s", model)
                break

        logger.error("Żaden model Gemini nie zwrócił poprawnej odpowiedzi")
        return _fallback("unavailable", language)
