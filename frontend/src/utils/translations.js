export const translations = {
  pl: {
    appTitle: "StockGuard AI",
    disclaimer: {
      title: "Zastrzeżenie",
      text: "Wyniki prezentowane w aplikacji (wykryte anomalie, wskaźniki techniczne oraz ocena i sugestie AI) mają charakter wyłącznie informacyjny i edukacyjny. Nie stanowią rekomendacji inwestycyjnej ani porady inwestycyjnej w rozumieniu przepisów o obrocie instrumentami finansowymi, w szczególności ustawy z dnia 29 lipca 2005 r. o obrocie instrumentami finansowymi oraz rozporządzenia (UE) nr 596/2014 (MAR). Decyzje inwestycyjne podejmujesz samodzielnie i na własne ryzyko.",
    },
    dashboard: {
      searchPlaceholder: "Wpisz symbol (np. NVDA, BTC-USD)",
      searchButton: "Szukaj i Analizuj",
      analyzing: "Analizowanie...",
      exportCSV: "Eksportuj CSV",
      exportPDF: "Pobierz Raport PDF",
      downloadReport: "Pobierz Wyniki",
      processing: "Przetwarzanie danych rynkowych i generowanie wniosków...",
      selectPrompt: "Wyszukaj ticker, aby rozpocząć analizę.",
      notFound: "Nie znaleziono danych dla symbolu",
      error: "Wystąpił błąd",
      providerError: "Źródło danych rynkowych jest chwilowo niedostępne. Spróbuj ponownie za chwilę.",
      exportError: "Nie udało się wygenerować pliku do pobrania.",
      subtitle: "Zaawansowana detekcja anomalii i interpretacja AI",
      marketSearch: "Wyszukiwanie rynku",
      analysisContext: "Kontekst analizy",
    },
    benchmark: {
      tabs: {
        standardAnalysis: "Standardowa Analiza",
        modelsBenchmark: "Benchmark Modeli"
      },
      loading: {
        title: "Inicjalizacja i weryfikacja algorytmów...",
        subtitle: "Wstrzykiwanie syntetycznych usterek. Modele głębokiego uczenia trenują struktury w locie!",
        walkForward: "Tryb bez wglądu w przyszłość doucza modele kilkadziesiąt razy na przebieg – może to potrwać do ok. 20 sekund (przy 2–5 latach danych do ok. 30 sekund)."
      },
      empty: {
        title: "Panel Ewaluacji Rozszerzonej Zablokowany",
        desc: "Benchmark pozwala w kontrolowanych warunkach zasymulować kryzysy w oparciu o najnowszą historię giełdy i zmierzyć realną siłę każdego z zaimplementowanych modeli (oraz ich połączenia) uczenia w jednym wspólnym środowisku testowym.",
        button: "Rozpocznij Mierzenie Osiągów"
      },
      header: {
        title: "Wydajność Modeli – Benchmark",
        subtitle: "Głęboka weryfikacja detektorów przed środowiskiem produkcyjnym.",
        barChart: "Wykres Słupkowy",
        radarChart: "Wykres Radarowy",
        metricF1: "Balans F1",
        metricPrecision: "Tylko Precyzja",
        metricRecall: "Bezwzględny Recall",
        csv: "⇩ CSV",
        runsInfo: "Wyniki to średnia ± odchylenie standardowe z {n} przebiegów z różnie rozmieszczonymi anomaliami."
      },
      insights: {
        title: "Podsumowanie i Rekomendacje Eksperckie",
        mainStart: "Biorąc pod uwagę wybrany przez Ciebie priorytet",
        mainMiddle: ", faworytem jest",
        mainValue: "osiągający",
        mainEnd: "skuteczności w tym konkretnym aspekcie.",
        precisionWinner: "Największa sprawność we wskazywaniu fałszywych alarmów (Precision):",
        recallWinner: "Zdolność by nie pominąć żadnej faktycznej luki (Recall):",
        tradeoffTitle: "Jak rozumieć Trade-Off?",
        tradeoffDesc: "Zwykle trudno mieć wysoki Recall przy wysokim Precision. Odporniejsze powiadomienia (Precision) skutkują przepuszczaniem pomniejszych krachów, natomiast duża czułość obrony (Recall) zasypie system powiadomieniami od drobnych rynkowych fluktuacji, stąd wybór F1-Score zawsze ubezpiecza balansem uśrednionym oba zachowania sztucznej inteligencji."
      },
      table: {
        model: "Platforma & Topologia",
        precision: "Precision",
        recall: "Recall",
        f1Score: "F1 Score",
        confusionMatrix: "Confusion Matrix",
        actions: "Akcje",
        leader: "⭐ LIDER",
        tp: "TP",
        fp: "FP",
        tn: "TN",
        fn: "FN",
        selectModel: "Analizuj tym Modelem",
        selectModelTitle: "Przełącz się na zakładkę analizy generując wykres bazujący na modelu:",
        calcError: "Błąd Obliczeń:",
        tooltipTp: "True Positives (Wykryto awarie poprawnie)",
        tooltipFp: "False Positives (Fałszywy alarm)",
        tooltipTn: "True Negatives (Poprawny brak anomalii)",
        tooltipFn: "False Negatives (Kryzys zignorowany)"
      },
      models: {
        isolation_forest_name: "Isolation Forest",
        isolation_forest_meta: "Szybki algorytm drzewiasty podziału przestrzeni; świetnie odizolowuje wyraźne giełdowe odchylenia od standardowych kwotowań.",
        lof_name: "Local Outlier Factor",
        lof_meta: "Analizuje lokalną gęstość punktów; potrafi wyłapać subtelniejsze anomalie i mikro-zawirowania wewnątrz dziennego trendu.",
        ocsvm_name: "One-Class SVM",
        ocsvm_meta: "Opiera się na nieliniowej granicy decyzyjnej; bardzo dobrze odnajduje się w przestrzeniach wielowymiarowych wokół punktów normy.",
        autoencoder_name: "PyTorch Autoencoder",
        autoencoder_meta: "Sztuczna sieć głębokiego uczenia. Świece o wielkim stopniu skompresowanego błędu rekonstrukcji wyrzucane są jako anomalie.",
        ensemble_name: "Ensemble (wszystkie modele)",
        ensemble_meta: "Łączy wszystkie cztery modele: ich wyniki sprowadzane są do wspólnej skali (odporny z-score) i uśredniane. Najstabilniejszy – rzadko najlepszy na łatwych danych, ale nigdy wyraźnie słaby."
      },
      scenario: {
        title: "Scenariusz anomalii",
        basic: "Podstawowy",
        extended: "Rozszerzony",
        basicDesc: "Pojedyncze, bardzo duże skoki ceny i wolumenu (3 odchylenia standardowe poziomu ceny z całego okresu). Łatwe do wykrycia – dobre do szybkiego sprawdzenia modeli.",
        extendedDesc: "Anomalie dopasowane do dziennej zmienności spółki, także rozłożone na kilka sesji: dryf ceny, wybuch zmienności, luka z powrotem. Trudniejsze i bliższe rzeczywistym zdarzeniom rynkowym."
      },
      byType: {
        title: "Wykrywalność według typu anomalii",
        desc: "Odsetek wstrzykniętych zdarzeń danego typu, które model wykrył (zdarzenie wielosesyjne jest wykryte, jeśli model oznaczył choć jedną z jego sesji). Najedź na nagłówek, aby zobaczyć opis typu.",
        events: "zdarzeń we wszystkich przebiegach"
      },
      types: {
        price_spike: "Skok ceny",
        price_drop: "Spadek ceny",
        volume_spike: "Skok wolumenu",
        gap_reversal: "Luka z powrotem",
        drift: "Dryf",
        volatility_burst: "Wybuch zmienności",
        price_spike_desc: "Jednodniowy, gwałtowny wzrost ceny zamknięcia.",
        price_drop_desc: "Jednodniowy, gwałtowny spadek ceny zamknięcia.",
        volume_spike_desc: "Jednodniowy, wielokrotny wzrost wolumenu obrotu przy zwykłej cenie.",
        gap_reversal_desc: "Otwarcie daleko od poprzedniego zamknięcia, po czym cena wraca do normy w ciągu dnia (nietypowa świeca).",
        drift_desc: "Pięć kolejnych sesji z umiarkowanym ruchem w tę samą stronę – żadna sesja osobno nie jest skrajna.",
        volatility_burst_desc: "Pięć kolejnych sesji z mniej więcej dwukrotnie większą zmiennością i szerszym zakresem dnia."
      },
      metrics: {
        precisionDesc: "Jak ufać alarmom? (Prawdziwe anomalie do sumy wszystkich ogłoszonych alarmów)",
        recallDesc: "Ile awarii wyłapał? (Wykryte anomalie do sumy faktycznych zaistniałych anomalii)",
        f1Desc: "Optymalny balans (Uśredniona wartość harmoniczna precyzji i czułości)",
        defaultDesc: "Wartość metryki porównawczej modeli."
      }
    },
    settings: {
      title: "Ustawienia analizy",
      model: "Model",
      period: "Okres danych",
      periodHint: "Dłuższy okres daje modelom więcej historii do nauki, ale analiza i benchmark trwają dłużej.",
      periods: {
        "6mo": "6 mies.",
        "1y": "1 rok",
        "2y": "2 lata",
        "5y": "5 lat"
      },
      sensitivity: "Czułość",
      sensitivityHint: "Odsetek sesji oznaczanych jako anomalie. Wyższa czułość = więcej alarmów, ale też więcej fałszywych. Benchmark wstrzykuje tyle samo anomalii.",
      apply: "Zastosuj ustawienia",
      reset: "Przywróć",
      close: "Zwiń ustawienia",
      pending: "Masz niezastosowane zmiany",
      pendingShort: "niezastosowane zmiany",
      searchHint: "Ustawienia zostaną użyte przy wyszukiwaniu spółki.",
      applyHint: "Zmień ustawienia i kliknij „Zastosuj ustawienia” – analiza zostanie wykonana raz, ze wszystkimi zmianami."
    },
    mode: {
      title: "Tryb detekcji",
      batch: "Analiza historyczna",
      walk_forward: "Bez wglądu w przyszłość",
      batchDesc: "Model uczy się na całym okresie naraz i ocenia każdą sesję z wiedzą o całej historii – także o sesjach późniejszych. Dobre do przeglądu historii, ale zawyża skuteczność względem pracy na bieżąco.",
      walk_forwardDesc: "Każda sesja oceniana jest modelem uczonym wyłącznie na wcześniejszych sesjach (douczanie co 10 sesji, przy długich okresach rzadziej), tak jak przy monitorowaniu rynku na bieżąco. Pierwsze 60 sesji służy tylko do nauki modelu i nie jest oceniane."
    },
    charts: {
      priceTitle: "Historia Cen i Sygnały AI",
      indicatorsTitle: "Wskaźniki Techniczne",
      closePrice: "Cena Zamknięcia",
      anomaly: "Anomalia",
      buySignal: "Sygnał Kupna",
      sellSignal: "Sygnał Sprzedaży",
      noData: "Brak danych do wyświetlenia",
      price: "Cena",
      signalLine: "Linia sygnału",
      bollingerTitle: "Wstęgi Bollingera i EMA",
      volatilityTitle: "Zmienność (ATR i odch. std.)",
      bbUpper: "Górna wstęga",
      bbLower: "Dolna wstęga",
    },
    assessment: {
      title: "Ocena Rynku AI",
      sentiment: "Sentyment",
      recommendation: "Rekomendacja",
      confidence: "Pewność",
      summary: "Podsumowanie Analizy",
      disclaimer: "Rekomendacja wygenerowana automatycznie przez model AI – nie stanowi rekomendacji inwestycyjnej ani porady inwestycyjnej.",
      values: {
        Bullish: "Byczy",
        Bearish: "Niedźwiedzi",
        Neutral: "Neutralny",
        Buy: "Kupuj",
        Sell: "Sprzedaj",
        Hold: "Trzymaj",
        High: "Wysoka",
        Medium: "Średnia",
        Low: "Niska",
      },
    },
    features: {
      return_1d: "Zmiana ceny (1 dzień)",
      return_3d: "Zmiana ceny (3 dni)",
      return_7d: "Zmiana ceny (7 dni)",
      momentum_5d: "Momentum (5 dni)",
      dist_to_ema20: "Odległość od EMA 20",
      drawdown: "Odległość od szczytu",
      volume_change: "Zmiana wolumenu (d/d)",
      volatility_change: "Zmiana zmienności (d/d)",
      volatility: "Zmienność 20 sesji (% ceny)",
      atr: "ATR (% ceny)",
      body: "Korpus świecy (% ceny)",
      upper_shadow: "Górny cień świecy (% ceny)",
      lower_shadow: "Dolny cień świecy (% ceny)",
      volume_ratio: "Wolumen vs średnia 20 sesji",
      rsi: "RSI",
      z_score_20: "Odchylenie od SMA 20 (σ)",
      bb_position: "Pozycja we wstęgach Bollingera"
    },
    table: {
      title: "Szczegółowe Dane",
      date: "Data",
      close: "Cena",
      score: "Wynik anomalii",
      status: "Status",
      anomaly: "ANOMALIA",
      normal: "Normalny",
      why: "Dlaczego anomalia?",
      typical: "typowo",
      onlyAnomalies: "Tylko anomalie",
      noAnomalies: "Brak anomalii w wybranym okresie.",
      explanationNote: "Przy anomaliach pokazujemy cechy sesji, które najbardziej odbiegały od normy – czyli od zachowania spółki w poprzednich ok. 6 miesiącach (▲ wyżej, ▼ niżej niż zwykle). To opis tego, co było nietypowe, a nie dokładny zapis rozumowania modelu."
    }
  },
  en: {
    appTitle: "StockGuard AI",
    disclaimer: {
      title: "Disclaimer",
      text: "The results shown in this application (detected anomalies, technical indicators and the AI assessment and suggestions) are for informational and educational purposes only. They do not constitute an investment recommendation or investment advice within the meaning of the regulations on trading in financial instruments, in particular the Polish Act of 29 July 2005 on Trading in Financial Instruments and Regulation (EU) No 596/2014 (MAR). You make investment decisions on your own and at your own risk.",
    },
    dashboard: {
      searchPlaceholder: "Enter symbol (e.g., NVDA, BTC-USD)",
      searchButton: "Search & Analyze",
      analyzing: "Analyzing...",
      exportCSV: "Export CSV",
      exportPDF: "Download PDF Report",
      downloadReport: "Download Results",
      processing: "Processing Market Data & Generating Insights...",
      selectPrompt: "Search for a ticker to begin analysis.",
      notFound: "No data found for symbol",
      error: "An error occurred",
      providerError: "The market data provider is temporarily unavailable. Please try again shortly.",
      exportError: "Failed to generate the download file.",
      subtitle: "Advanced Anomaly Detection & AI Interpretation",
      marketSearch: "Market Search",
      analysisContext: "Analysis Context",
    },
    benchmark: {
      tabs: {
        standardAnalysis: "Standard Analysis",
        modelsBenchmark: "Models Benchmark"
      },
      loading: {
        title: "Initializing and verifying algorithms...",
        subtitle: "Injecting synthetic anomalies. Deep learning models train structures on the fly!",
        walkForward: "No look-ahead mode retrains models dozens of times per run – this may take up to ~20 seconds (up to ~30 seconds for 2–5 years of data)."
      },
      empty: {
        title: "Extended Evaluation Panel Locked",
        desc: "The benchmark allows you to simulate market crashes in controlled conditions based on recent history to measure the real strength of each implemented AI model in a common test environment.",
        button: "Start Performance Measuring"
      },
      header: {
        title: "Models Benchmark Performance",
        subtitle: "Deep verification of detectors before the production environment.",
        barChart: "Bar Chart",
        radarChart: "Radar Chart",
        metricF1: "F1 Balance",
        metricPrecision: "Precision Only",
        metricRecall: "Absolute Recall",
        csv: "⇩ CSV",
        runsInfo: "Results are mean ± standard deviation over {n} runs with differently placed anomalies."
      },
      insights: {
        title: "Expert Summary & Recommendations",
        mainStart: "Considering your selected priority",
        mainMiddle: ", the absolute favorite is",
        mainValue: "reaching",
        mainEnd: "efficiency in this specific aspect.",
        precisionWinner: "Highest efficiency in avoiding false alarms (Precision):",
        recallWinner: "Ability to not miss any actual drop (Recall):",
        tradeoffTitle: "Understanding the Trade-Off",
        tradeoffDesc: "Usually it is hard to maintain high Recall with high Precision. Stricter alerts (Precision) result in missing minor crashes, while high defense sensitivity (Recall) floods the system with alerts from minor fluctuations. Hence, selecting F1-Score always ensures a balanced average of both machine learning properties."
      },
      table: {
        model: "Platform & Topology",
        precision: "Precision",
        recall: "Recall",
        f1Score: "F1 Score",
        confusionMatrix: "Confusion Matrix",
        actions: "Actions",
        leader: "⭐ LEADER",
        tp: "TP",
        fp: "FP",
        tn: "TN",
        fn: "FN",
        selectModel: "Analyze with Model",
        selectModelTitle: "Switch to Analysis tab generating chart based on the model:",
        calcError: "Calculation Error:",
        tooltipTp: "True Positives (Correctly detected anomalies)",
        tooltipFp: "False Positives (False alarms)",
        tooltipTn: "True Negatives (Correct normal data)",
        tooltipFn: "False Negatives (Missed crashes)"
      },
      models: {
        isolation_forest_name: "Isolation Forest",
        isolation_forest_meta: "Fast tree-based space partitioning algorithm; excellently isolates clear market deviations.",
        lof_name: "Local Outlier Factor",
        lof_meta: "Analyzes local density; capable of catching subtle anomalies and micro-fluctuations within the daily trend.",
        ocsvm_name: "One-Class SVM",
        ocsvm_meta: "Based on nonlinear decision boundaries; performs exceptionally well in high-dimensional spaces near normal points.",
        autoencoder_name: "PyTorch Autoencoder",
        autoencoder_meta: "Artificial deep learning network. Candles with massive compressed reconstruction error are flagged as anomalies.",
        ensemble_name: "Ensemble (all models)",
        ensemble_meta: "Combines all four models: their scores are put on a common scale (robust z-score) and averaged. The most stable – rarely the best on easy data, but never clearly weak."
      },
      scenario: {
        title: "Anomaly scenario",
        basic: "Basic",
        extended: "Extended",
        basicDesc: "Single, very large price and volume jumps (3 standard deviations of the price level over the whole period). Easy to detect – good for a quick model check.",
        extendedDesc: "Anomalies scaled to the stock's daily volatility, including multi-session events: price drift, volatility burst, gap with reversal. Harder and closer to real market events."
      },
      byType: {
        title: "Detection rate by anomaly type",
        desc: "Share of injected events of each type detected by the model (a multi-session event counts as detected if the model flagged at least one of its sessions). Hover over a header to see the type description.",
        events: "events across all runs"
      },
      types: {
        price_spike: "Price spike",
        price_drop: "Price drop",
        volume_spike: "Volume spike",
        gap_reversal: "Gap & reversal",
        drift: "Drift",
        volatility_burst: "Volatility burst",
        price_spike_desc: "A sudden one-day jump in the closing price.",
        price_drop_desc: "A sudden one-day drop in the closing price.",
        volume_spike_desc: "A one-day multi-fold increase in trading volume at a normal price.",
        gap_reversal_desc: "The session opens far from the previous close, then the price returns to normal during the day (unusual candle).",
        drift_desc: "Five consecutive sessions with moderate moves in the same direction – no single session is extreme.",
        volatility_burst_desc: "Five consecutive sessions with roughly doubled volatility and a wider daily range."
      },
      metrics: {
        precisionDesc: "How much to trust alerts? (True anomalies out of all declared alarms)",
        recallDesc: "How many crashes caught? (Detected anomalies out of all actual anomalies)",
        f1Desc: "Optimal balance (Harmonic mean of precision and recall)",
        defaultDesc: "Comparative metric value."
      }
    },
    settings: {
      title: "Analysis settings",
      model: "Model",
      period: "Data period",
      periodHint: "A longer period gives the models more history to learn from, but analysis and benchmark take longer.",
      periods: {
        "6mo": "6 mo",
        "1y": "1 year",
        "2y": "2 years",
        "5y": "5 years"
      },
      sensitivity: "Sensitivity",
      sensitivityHint: "Share of sessions flagged as anomalies. Higher sensitivity = more alerts, but also more false ones. The benchmark injects the same share of anomalies.",
      apply: "Apply settings",
      reset: "Revert",
      close: "Collapse settings",
      pending: "You have unapplied changes",
      pendingShort: "unapplied changes",
      searchHint: "These settings will be used when you search for a stock.",
      applyHint: "Change the settings and click “Apply settings” – the analysis runs once, with all changes."
    },
    mode: {
      title: "Detection mode",
      batch: "Historical analysis",
      walk_forward: "No look-ahead",
      batchDesc: "The model learns from the whole period at once and scores each session knowing the entire history – including later sessions. Good for reviewing history, but it overstates performance compared to live monitoring.",
      walk_forwardDesc: "Each session is scored by a model trained only on earlier sessions (retrained every 10 sessions, less often for long periods), just like live market monitoring. The first 60 sessions are used only for training and are not scored."
    },
    charts: {
      priceTitle: "Price History & AI Signals",
      indicatorsTitle: "Technical Indicators",
      closePrice: "Close Price",
      anomaly: "Anomaly",
      buySignal: "Buy Signal",
      sellSignal: "Sell Signal",
      noData: "No data to display",
      price: "Price",
      signalLine: "Signal",
      bollingerTitle: "Bollinger Bands & EMA",
      volatilityTitle: "Volatility (ATR & StdDev)",
      bbUpper: "BB Upper",
      bbLower: "BB Lower",
    },
    assessment: {
      title: "AI Market Assessment",
      sentiment: "Sentiment",
      recommendation: "Recommendation",
      confidence: "Confidence",
      summary: "Analysis Summary",
      disclaimer: "Recommendation generated automatically by an AI model – it is not an investment recommendation or investment advice.",
      values: {
        Bullish: "Bullish",
        Bearish: "Bearish",
        Neutral: "Neutral",
        Buy: "Buy",
        Sell: "Sell",
        Hold: "Hold",
        High: "High",
        Medium: "Medium",
        Low: "Low",
      },
    },
    features: {
      return_1d: "Price change (1 day)",
      return_3d: "Price change (3 days)",
      return_7d: "Price change (7 days)",
      momentum_5d: "Momentum (5 days)",
      dist_to_ema20: "Distance from EMA 20",
      drawdown: "Distance from peak",
      volume_change: "Volume change (d/d)",
      volatility_change: "Volatility change (d/d)",
      volatility: "20-session volatility (% of price)",
      atr: "ATR (% of price)",
      body: "Candle body (% of price)",
      upper_shadow: "Upper shadow (% of price)",
      lower_shadow: "Lower shadow (% of price)",
      volume_ratio: "Volume vs 20-session average",
      rsi: "RSI",
      z_score_20: "Deviation from SMA 20 (σ)",
      bb_position: "Position within Bollinger Bands"
    },
    table: {
      title: "Detailed Data",
      date: "Date",
      close: "Close",
      score: "Anomaly Score",
      status: "Status",
      anomaly: "ANOMALY",
      normal: "Normal",
      why: "Why an anomaly?",
      typical: "typically",
      onlyAnomalies: "Anomalies only",
      noAnomalies: "No anomalies in the selected period.",
      explanationNote: "For anomalies we show the session features that deviated most from normal – i.e. from the stock's behaviour over the previous ~6 months (▲ higher, ▼ lower than usual). This describes what was unusual, not the exact reasoning of the model."
    }
  }
};

// Zwraca tłumaczenie dla klucza w notacji kropkowej (np. 'dashboard.error') lub sam klucz, gdy go brak
export const translate = (language, key) => {
  let value = translations[language];
  for (const k of key.split('.')) {
    if (value == null) break;
    value = value[k];
  }
  return typeof value === 'string' ? value : key;
};
