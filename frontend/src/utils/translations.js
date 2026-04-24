export const translations = {
  pl: {
    appTitle: "StockGuard AI",
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
      standardAnalysis: "Standardowa Analiza",
      modelsBenchmark: "Benchmark Modeli",
    },
    benchmark: {
      tabs: {
        standardAnalysis: "Standardowa Analiza",
        modelsBenchmark: "Benchmark Modeli"
      },
      loading: {
        title: "Inicjalizacja i weryfikacja algorytmów...",
        subtitle: "Wstrzykiwanie syntetycznych usterek. Modele głębokiego uczenia trenują struktury w locie!"
      },
      empty: {
        title: "Panel Ewaluacji Rozszerzonej Zablokowany",
        desc: "Benchmark pozwala w kontrolowanych warunkach zasymulować kryzysy w oparciu o najnowszą historię giełdy i zmierzyć realną siłę każdego z 4 zaimplementowanych modeli uczenia w jednym wspólnym środowisku testowym.",
        button: "Rozpocznij Mierzenie Osiągów"
      },
      header: {
        title: "Models Benchmark Performance",
        subtitle: "Głęboka weryfikacja detektorów przed środowiskiem produkcyjnym.",
        barChart: "Wykres Słupkowy",
        radarChart: "Wykres Radarowy",
        metricF1: "Balans F1",
        metricPrecision: "Tylko Precyzja",
        metricRecall: "Bezwzględny Recall",
        csv: "⇩ CSV"
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
        autoencoder_meta: "Sztuczna sieć głębokiego uczenia. Świece o wielkim stopniu skompresowanego błędu rekonstrukcji wyrzucane są jako anomalie."
      },
      metrics: {
        precisionDesc: "Jak ufać alarmom? (Prawdziwe anomalie do sumy wszystkich ogłoszonych alarmów)",
        recallDesc: "Ile awarii wyłapał? (Wykryte anomalie do sumy faktycznych zaistniałych anomalii)",
        f1Desc: "Optymalny balans (Uśredniona wartość harmoniczna precyzji i czułości)",
        defaultDesc: "Wartość metryki porównawczej modeli."
      }
    },
    charts: {
      priceTitle: "Historia Cen i Sygnały AI",
      indicatorsTitle: "Wskaźniki Techniczne",
      closePrice: "Cena Zamknięcia",
      anomaly: "Anomalia",
      buySignal: "Sygnał Kupna",
    },
    assessment: {
      title: "Ocena Rynku AI",
      sentiment: "Sentyment",
      recommendation: "Rekomendacja",
      confidence: "Pewność",
      summary: "Podsumowanie Analizy",
    },
    table: {
      title: "Szczegółowe Dane",
      date: "Data",
      close: "Cena",
      features: "Cechy (Zwrot/Zmienność)",
      status: "Status",
      anomaly: "ANOMALIA",
      normal: "Normalny",
    }
  },
  en: {
    appTitle: "StockGuard AI",
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
      standardAnalysis: "Standard Analysis",
      modelsBenchmark: "Models Benchmark",
    },
    benchmark: {
      tabs: {
        standardAnalysis: "Standard Analysis",
        modelsBenchmark: "Models Benchmark"
      },
      loading: {
        title: "Initializing and verifying algorithms...",
        subtitle: "Injecting synthetic anomalies. Deep learning models train structures on the fly!"
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
        csv: "⇩ CSV"
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
        autoencoder_meta: "Artificial deep learning network. Candles with massive compressed reconstruction error are flagged as anomalies."
      },
      metrics: {
        precisionDesc: "How much to trust alerts? (True anomalies out of all declared alarms)",
        recallDesc: "How many crashes caught? (Detected anomalies out of all actual anomalies)",
        f1Desc: "Optimal balance (Harmonic mean of precision and recall)",
        defaultDesc: "Comparative metric value."
      }
    },
    charts: {
      priceTitle: "Price History & AI Signals",
      indicatorsTitle: "Technical Indicators",
      closePrice: "Close Price",
      anomaly: "Anomaly",
      buySignal: "Buy Signal",
    },
    assessment: {
      title: "AI Market Assessment",
      sentiment: "Sentiment",
      recommendation: "Recommendation",
      confidence: "Confidence",
      summary: "Analysis Summary",
    },
    table: {
      title: "Detailed Data",
      date: "Date",
      close: "Close",
      features: "Features (Return/Vol)",
      status: "Status",
      anomaly: "ANOMALY",
      normal: "Normal",
    }
  }
};
