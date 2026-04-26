# StockGuard AI 📈🤖

StockGuard AI to zaawansowana aplikacja webowa do monitorowania rynków finansowych, wykrywania anomalii w danych giełdowych oraz generowania automatycznych interpretacji za pomocą sztucznej inteligencji.

## 🚀 Kluczowe Funkcje

- **Monitorowanie w czasie rzeczywistym**: Pobieranie danych giełdowych bezpośrednio z `yfinance`.
- **Wykrywanie Anomalii (Wielomodelowe)**: Integracja wielu zaawansowanych modeli uczenia maszynowego (m.in. Isolation Forest, LOF, One-Class SVM, Autoencoder) w celu precyzyjnej identyfikacji nietypowych ruchów cenowych.
- **Ewaluacja i Benchmarking Modeli**: Wbudowany moduł ewaluacji pozwalający na bieżąco oceniać i porównywać skuteczność poszczególnych modeli ML z użyciem dedykowanych endpointów.
- **Wskaźniki Techniczne**: Automatyczne obliczanie m.in. RSI, MACD, Wstęg Bollingera, EMA oraz ATR.
- **Interpretacja AI**: Generowanie raportów i rekomendacji (Kup/Sprzedaj) przy wsparciu modeli językowych (Google Gemini AI).
- **Rozbudowany Dashboard i Wykresy**: Interfejs wizualizujący dane cenowe, wykryte anomalie, wydajność modeli oraz sygnały wejścia.
- **Wielojęzyczność (i18n)**: Pełne wsparcie dla wielojęzycznego interfejsu (m.in. j. polski i j. angielski) dzięki zintegrowanemu Providerowi Języków.

## 🛠 Technologie

- **Backend**: FastAPI (Python 3.10)
- **Frontend**: React + Vite (Tailwind CSS, Recharts, i18next do wielojęzyczności)
- **ML/AI**: Scikit-Learn (m.in. Isolation Forest, LOF, SVM), PyTorch/TensorFlow (dla Autoencoderów), Google Gemini AI
- **Infrastruktura**: Docker, PostgreSQL
- **Jakość kodu**: Wdrożone testy jednostkowe i integracyjne dla API.

---

## 💻 Instrukcja Uruchomienia

### Szybki Start (Docker) 🐳

Najszybsza metoda uruchomienia całej infrastruktury (Backend + Frontend + Baza Danych).

1. **Utwórz plik `.env`** w katalogu `/backend/` z kluczem API:
   ```env
   GEMINI_API_KEY="twój_google_ai_studio_api_key_tutaj"
   ```
2. **Upewnij się, że masz zainstalowany Docker Desktop.**
3. **Uruchom projekt jedną komendą:**
   ```powershell
   docker-compose up --build
   ```
4. **Dostęp do aplikacji:**
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Sposób 2: Uruchomienie lokalne (Manualne)

Jeśli nie chcesz korzystać z Dockera, możesz uruchomić komponenty osobno.

#### Windows

1. **Konfiguracja klucza API**:
   - Utwórz plik `backend/.env` i dodaj linię: `GEMINI_API_KEY="twój_klucz_tutaj"`

2. **Backend**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   cd backend
   uvicorn main:app --reload
   ```
3. **Frontend**:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

#### Linux / macOS

1. **Konfiguracja klucza API**:
   - Utwórz plik `backend/.env` i dodaj linię: `GEMINI_API_KEY="twój_klucz_tutaj"`

2. **Backend**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd backend
   uvicorn main:app --reload
   ```
3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📂 Struktura Projektu

- `/backend` - Serwer API, modele ML z modułem ewaluacji, testy jednostkowe/integracyjne oraz usługi AI.
- `/frontend` - Interfejs użytkownika, i18n, interaktywne wykresy i rozbudowany dashboard.
- `docker-compose.yml` - Konfiguracja całego środowiska.

---

_Autor: karmauh_
