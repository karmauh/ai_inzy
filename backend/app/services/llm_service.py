from typing import List, Dict, Any
import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    @staticmethod
    def generate_assessment(data: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], ticker_info: Dict[str, Any] = None, language: str = 'pl') -> Dict[str, Any]:
        """
        Generuje ocenę i interpretację wyników analizy używając modelu LLM (Google Gemini).
        """
        if not anomalies:
            return {
                "sentiment": "Neutral",
                "recommendation": "Hold",
                "summary": "No data available." if language == 'en' else "Brak danych do analizy.",
                "confidence": "Low"
            }
            
        last_point = anomalies[-1]
        
        ticker_str = f"Ticker: {ticker_info.get('symbol', 'N/A')} ({ticker_info.get('name', 'N/A')})" if ticker_info else "Ticker: Nieznany"
        
        # Pobieranie parametryzacji
        def fmt(val):
            return f"{val:.2f}" if isinstance(val, (int, float)) else str(val)

        close = fmt(last_point.get('close', 'N/A'))
        rsi = fmt(last_point.get('rsi', 'N/A'))
        macd = fmt(last_point.get('macd', 'N/A'))
        macd_signal = fmt(last_point.get('macd_signal', 'N/A'))
        ema_20 = fmt(last_point.get('ema_20', 'N/A'))
        ema_50 = fmt(last_point.get('ema_50', 'N/A'))
        atr = fmt(last_point.get('atr', 'N/A'))
        bb_upper = fmt(last_point.get('bb_upper', 'N/A'))
        bb_lower = fmt(last_point.get('bb_lower', 'N/A'))
        is_anomaly = last_point.get('is_anomaly', False)
        
        lang_instruction = "angielskim" if language == "en" else "polskim"

        # Główny prompt przekazany przez użytkownika
        system_prompt = f"""
Jesteś asystentem-analitykiem rynków finansowych w aplikacji StockGuard AI.
Otrzymujesz przetworzone dane techniczne dla jednego instrumentu (akcja, ETF lub indeks): ceny, wskaźniki techniczne (RSI, MACD, Bollinger Bands, EMA, ATR), informację o anomaliach oraz podstawowe metadane (ticker, interwał, zakres dat).
Twoim zadaniem jest:

- Krótko podsumować aktualną sytuację rynkową instrumentu.
- Zinterpretować wskaźniki techniczne (co oznacza poziom RSI, sygnały MACD, wybicia poza wstęgi Bollingera, zmienność z ATR, kierunek trendu na podstawie EMA).
- Wspomnieć o wykrytych anomaliach (np. nietypowe wolumeny, gwałtowne ruchy cenowe) i co mogą sugerować.
- Na końcu sformułować prostą rekomendację w formacie: Rekomendacja: [Kupuj / Trzymaj / Sprzedaj] wraz z 2–3 zdaniami uzasadnienia.

Zasady:
- Pisz formatując kluczowe słowa w tekście (używaj znaczników Markdown `**pogrubienie**` do wyróżniania mniejszych pojęć zamiast kropek).
- Przejrzyście podziel odpowiedź dokładnie na 2 do 3 akapitów, nie twórz jednolitej ściany tekstu.
- Używaj prostego języka, ale z poprawną terminologią techniczną.
- Nie podawaj konkretnych cen docelowych ani gwarancji wyniku.
- Jeśli dane są sprzeczne lub niejednoznaczne, wyraźnie to zaznacz i wybierz bardziej zachowawczą rekomendację.
- Jeśli brakuje jakiegoś wskaźnika, powiedz „brak danych” zamiast zgadywać.
- Odpowiadaj w języku {lang_instruction}, ale nazwy wskaźników (RSI, MACD, itp.) zostaw w oryginale.

KONIECZNIE NA SAMYM KOŃCU SWOJEJ ODPOWIEDZI WYGENERUJ ODDZIELNĄ SEKCJE W FORMACIE JSON (aby system mógł ją łatwo parsować do interfejsu TheDashboard):
```json
{{
  "sentiment": "Byczy / Niedźwiedzi / Neutralny" (lub odpowiednik w EN jeśli język to EN),
  "recommendation": "Kupuj / Trzymaj / Sprzedaj" (lub Buy / Hold / Sell jeśli EN),
  "confidence": "Wysoka / Średnia / Niska" (lub High / Medium / Low jeśli EN)
}}
```

Dane techniczne rynkowe:
-------------------------
{ticker_str}
Ostatnia cena zamknięcia: {close}
RSI(14): {rsi}
MACD: {macd} (Signal: {macd_signal})
EMA(20): {ema_20}
EMA(50): {ema_50}
ATR(14): {atr}
Wstęgi Bollingera (Górna/Dolna): {bb_upper} / {bb_lower}
Czy wykryto anomalię statystyczną na ostatniej sesji?: {'Tak' if is_anomaly else 'Nie'}
-------------------------
"""

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "sentiment": "Neutral",
                "recommendation": "Hold",
                "summary": "Błąd: Brak klucza API (GEMINI_API_KEY) dla modelu LLM w pliku .env.",
                "confidence": "Low"
            }

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        request_data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": system_prompt
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=request_data)
            response.raise_for_status()
            resp_json = response.json()
            
            # Wypakowywanie odpowiedzi Gemini
            text_output = resp_json["candidates"][0]["content"]["parts"][0]["text"]
            
            # Próba parsowania JSON z formatowania LLM-a
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text_output, re.DOTALL | re.IGNORECASE)
            
            if json_match:
                parsed_json = json.loads(json_match.group(1))
                sentiment = parsed_json.get("sentiment", "Neutral")
                recommendation = parsed_json.get("recommendation", "Hold")
                confidence = parsed_json.get("confidence", "Medium")
                # Oddzielenie tresci raportu od bloku technicznego JSON
                raw_summary = text_output[:json_match.start()].strip()
            else:
                raw_summary = text_output.strip()
                sentiment = "Neutral"
                confidence = "Medium"
                
                # Zgrzebny Fallback
                if "Kupuj" in raw_summary or "Kup" in raw_summary or "Buy" in raw_summary:
                    recommendation = "Kupuj" if language == "pl" else "Buy"
                elif "Sprzedaj" in raw_summary or "Sell" in raw_summary:
                    recommendation = "Sprzedaj" if language == "pl" else "Sell"
                else:
                    recommendation = "Trzymaj" if language == "pl" else "Hold"

            return {
                "sentiment": sentiment,
                "recommendation": recommendation,
                "summary": raw_summary,
                "confidence": confidence
            }
            
        except Exception as e:
            print("Błąd łączenia z Gemini API:", str(e))
            return {
                "sentiment": "Neutral",
                "recommendation": "Hold",
                "summary": f"Nie udało się połączyć z usługą AI: {str(e)}",
                "confidence": "Low"
            }
