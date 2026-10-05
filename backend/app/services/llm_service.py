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
    def build_prompt(last_point: Dict[str, Any], ticker_info: Optional[Dict[str, Any]], language: str) -> str:
        def fmt(val):
            return f"{val:.2f}" if isinstance(val, (int, float)) and not isinstance(val, bool) else "brak danych"

        ticker_str = (
            f"Ticker: {ticker_info.get('symbol', 'N/A')} ({ticker_info.get('name', 'N/A')})"
            if ticker_info else "Ticker: Nieznany"
        )
        lang_instruction = "angielskim" if language == "en" else "polskim"
        is_anomaly = last_point.get('is_anomaly', False)

        return f"""
Jesteś asystentem-analitykiem rynków finansowych w aplikacji StockGuard AI.
Otrzymujesz przetworzone dane techniczne dla jednego instrumentu (akcja, ETF lub indeks): cenę, wskaźniki techniczne (RSI, MACD, Bollinger Bands, EMA, ATR) oraz informację o anomalii statystycznej.
Twoim zadaniem jest:

- Krótko podsumować aktualną sytuację rynkową instrumentu.
- Zinterpretować wskaźniki techniczne (co oznacza poziom RSI, sygnały MACD, wybicia poza wstęgi Bollingera, zmienność z ATR, kierunek trendu na podstawie EMA).
- Wspomnieć o wykrytej anomalii (jeśli występuje) i co może sugerować.
- Na końcu sformułować prostą rekomendację wraz z 2–3 zdaniami uzasadnienia.

Zasady:
- Wyróżniaj kluczowe pojęcia znacznikami Markdown `**pogrubienie**`.
- Podziel odpowiedź na 2 do 3 akapitów, nie twórz jednolitej ściany tekstu.
- Używaj prostego języka, ale z poprawną terminologią techniczną.
- Nie podawaj konkretnych cen docelowych ani gwarancji wyniku.
- Jeśli dane są sprzeczne lub niejednoznaczne, wyraźnie to zaznacz i wybierz bardziej zachowawczą rekomendację.
- Jeśli brakuje jakiegoś wskaźnika, powiedz „brak danych” zamiast zgadywać.
- Odpowiadaj w języku {lang_instruction}, ale nazwy wskaźników (RSI, MACD, itp.) zostaw w oryginale.

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
    def generate_assessment(results: List[Dict[str, Any]], ticker_info: Optional[Dict[str, Any]] = None, language: str = 'pl') -> Dict[str, Any]:
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

        prompt = LLMService.build_prompt(results[-1], ticker_info, language)

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
