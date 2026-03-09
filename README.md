# StockGuard AI 📈🤖

StockGuard AI to zaawansowana aplikacja webowa do monitorowania rynków finansowych, wykrywania anomalii w danych giełdowych oraz generowania automatycznych interpretacji za pomocą sztucznej inteligencji.

## 🚀 Kluczowe Funkcje

- **Monitorowanie w czasie rzeczywistym**: Pobieranie danych giełdowych bezpośrednio z `yfinance`.
- **Wykrywanie Anomalii**: Wykorzystanie modelu _Isolation Forest_ do identyfikacji nietypowych ruchów cenowych.
- **Wskaźniki Techniczne**: Automatyczne obliczanie RSI, MACD, Wstęg Bollingera, EMA oraz ATR.
- **Interpretacja AI**: Generowanie raportów i rekomendacji (Kup/Sprzedaj) w języku polskim i angielskim.
- **Interaktywne Wykresy**: Wizualizacja danych cenowych wraz z zaznaczonymi anomaliami i sygnałami wejścia.

## 🛠 Technologie

- **Backend**: FastAPI (Python 3.10)
- **Frontend**: React + Vite (Tailwind CSS, Recharts)
- **ML/AI**: Scikit-Learn, OpenAI/LLM Integration
- **Infrastruktura**: Docker, PostgreSQL

---

## 💻 Instrukcja Uruchomienia

### Sposób 1: Docker (Zalecane - wszystkie systemy)

Wymagany zainstalowany [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/karmauh/ai_inzy.git
   cd ai_inzy
   ```
2. Uruchom kontenery:
   ```bash
   docker-compose up --build
   ```
3. Aplikacja dostępna pod adresem: `http://localhost:5173`

---

### Sposób 2: Uruchomienie lokalne

#### Windows

1. **Backend**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r backend/requirements.txt
   cd backend
   uvicorn main:app --reload
   ```
2. **Frontend**:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

#### Linux / macOS

1. **Backend**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   cd backend
   uvicorn main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📂 Struktura Projektu

- `/backend` - Serwer API, modele ML i usługi AI.
- `/frontend` - Interfejs użytkownika z interaktywnymi wykresami.
- `docker-compose.yml` - Konfiguracja całego środowiska.

---

_Autor: karmauh_
