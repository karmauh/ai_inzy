export const translations = {
  pl: {
    appTitle: "StockGuard AI",
    disclaimer: {
      title: "Zastrzeżenie",
      text: "Wyniki prezentowane w aplikacji (wykryte anomalie, wskaźniki techniczne oraz ocena i sugestie AI) mają charakter wyłącznie informacyjny i edukacyjny. Nie stanowią rekomendacji inwestycyjnej ani porady inwestycyjnej w rozumieniu przepisów o obrocie instrumentami finansowymi, w szczególności ustawy z dnia 29 lipca 2005 r. o obrocie instrumentami finansowymi oraz rozporządzenia (UE) nr 596/2014 (MAR). Decyzje inwestycyjne podejmujesz samodzielnie i na własne ryzyko.",
    },
    dashboard: {
      searchPlaceholder: "Wpisz symbol (np. NVDA, BTC-USD)",
      searchButton: "Szukaj i analizuj",
      analyzing: "Analizowanie...",
      exportCSV: "Eksportuj CSV",
      exportPDF: "Pobierz raport PDF",
      downloadReport: "Pobierz wyniki",
      processing: "Przetwarzanie danych rynkowych i generowanie oceny...",
      selectPrompt: "Wyszukaj symbol instrumentu, aby rozpocząć analizę.",
      notFound: "Nie znaleziono danych dla symbolu",
      error: "Wystąpił błąd",
      providerError: "Źródło danych rynkowych jest chwilowo niedostępne. Spróbuj ponownie za chwilę.",
      exportError: "Nie udało się wygenerować pliku do pobrania.",
      subtitle: "Detekcja anomalii w danych giełdowych z interpretacją modelu językowego",
      marketSearch: "Wyszukiwanie instrumentu",
      analysisContext: "Kontekst analizy",
    },
    benchmark: {
      tabs: {
        standardAnalysis: "Analiza instrumentu",
        modelsBenchmark: "Porównanie modeli"
      },
      loading: {
        title: "Ocena modeli w toku...",
        subtitle: "Wprowadzanie syntetycznych anomalii i ocena modeli w kolejnych przebiegach.",
        walkForward: "W trybie bez wglądu w przyszłość modele są douczane kilkadziesiąt razy w każdym przebiegu, dlatego ocena może potrwać do ok. 20 sekund (przy 2–5 latach danych do ok. 30 sekund)."
      },
      empty: {
        title: "Porównanie skuteczności modeli",
        desc: "Do notowań analizowanego instrumentu wprowadzane są syntetyczne anomalie o znanym położeniu, a następnie sprawdzane jest, w jakim stopniu wykrywa je każdy z pięciu modeli. Wynik pozwala wybrać model najlepiej dopasowany do danego instrumentu.",
        button: "Uruchom porównanie modeli"
      },
      header: {
        title: "Porównanie skuteczności modeli",
        subtitle: "Precyzja, pełność i miara F1 na danych z syntetycznymi anomaliami.",
        barChart: "Wykres słupkowy",
        radarChart: "Wykres radarowy",
        metricF1: "Miara F1",
        metricPrecision: "Precyzja",
        metricRecall: "Pełność",
        csv: "Eksportuj CSV",
        runsInfo: "Wyniki to średnia ± odchylenie standardowe z {n} przebiegów z różnie rozmieszczonymi anomaliami."
      },
      insights: {
        title: "Podsumowanie wyników",
        mainStart: "Według wybranej miary",
        mainMiddle: " najlepszy wynik uzyskał model",
        mainValue: "– wartość",
        mainEnd: "dla analizowanego instrumentu.",
        precisionWinner: "Najwyższa precyzja (najmniej fałszywych alarmów):",
        recallWinner: "Najwyższa pełność (najmniej pominiętych anomalii):",
        tradeoffTitle: "Kompromis między precyzją a pełnością",
        tradeoffDesc: "Zwiększenie pełności zwykle obniża precyzję: model wykrywający więcej anomalii zgłasza też więcej fałszywych alarmów. Miara F1, będąca średnią harmoniczną obu miar, pozwala porównać modele z uwzględnieniem obu tych aspektów."
      },
      table: {
        model: "Model",
        precision: "Precyzja",
        recall: "Pełność",
        f1Score: "Miara F1",
        confusionMatrix: "Macierz pomyłek",
        actions: "Akcje",
        leader: "NAJLEPSZY",
        tp: "TP",
        fp: "FP",
        tn: "TN",
        fn: "FN",
        selectModel: "Analizuj tym modelem",
        selectModelTitle: "Przejdź do zakładki analizy i wykonaj analizę modelem:",
        calcError: "Błąd obliczeń:",
        tooltipTp: "Prawdziwie pozytywne (poprawnie wykryte anomalie)",
        tooltipFp: "Fałszywie pozytywne (fałszywe alarmy)",
        tooltipTn: "Prawdziwie negatywne (poprawnie rozpoznane sesje typowe)",
        tooltipFn: "Fałszywie negatywne (pominięte anomalie)"
      },
      models: {
        isolation_forest_name: "Isolation Forest",
        isolation_forest_meta: "Izoluje obserwacje losowymi podziałami przestrzeni cech; skuteczny przy dużych, pojedynczych zmianach ceny.",
        lof_name: "Local Outlier Factor",
        lof_meta: "Porównuje lokalną gęstość obserwacji z jej otoczeniem; wykrywa sesje nietypowe na tle okresu o podobnej zmienności. Model domyślny.",
        ocsvm_name: "One-Class SVM",
        ocsvm_meta: "Wyznacza nieliniową granicę obszaru typowych obserwacji; wrażliwy na dobór parametrów.",
        autoencoder_name: "Autoenkoder (PyTorch)",
        autoencoder_meta: "Sieć neuronowa odtwarzająca cechy sesji; sesje o dużym błędzie rekonstrukcji uznawane są za anomalie.",
        ensemble_name: "Model zespołowy (wszystkie modele)",
        ensemble_meta: "Uśrednia znormalizowane wyniki czterech modeli; zmniejsza ryzyko pominięcia anomalii określonego typu, lecz osłabia sygnał najlepszego z nich."
      },
      scenario: {
        title: "Scenariusz anomalii",
        basic: "Podstawowy",
        extended: "Rozszerzony",
        basicDesc: "Pojedyncze, duże zmiany ceny lub wolumenu (około 3 odchyleń standardowych poziomu ceny z całego okresu). Łatwe do wykrycia.",
        extendedDesc: "Anomalie dopasowane do dziennej zmienności instrumentu, także obejmujące kilka sesji: dryf ceny, wybuch zmienności, luka z odwróceniem. Trudniejsze i bliższe zdarzeniom rzeczywistym."
      },
      byType: {
        title: "Wykrywalność według typu anomalii",
        desc: "Odsetek wprowadzonych zdarzeń danego typu, które model wykrył (zdarzenie wielosesyjne jest wykryte, jeśli model wskazał co najmniej jedną z jego sesji). Wskaż nagłówek kursorem, aby zobaczyć opis typu.",
        events: "zdarzeń we wszystkich przebiegach"
      },
      types: {
        price_spike: "Skok ceny",
        price_drop: "Spadek ceny",
        volume_spike: "Skok wolumenu",
        gap_reversal: "Luka z odwróceniem",
        drift: "Dryf",
        volatility_burst: "Wybuch zmienności",
        price_spike_desc: "Jednodniowy, gwałtowny wzrost ceny zamknięcia.",
        price_drop_desc: "Jednodniowy, gwałtowny spadek ceny zamknięcia.",
        volume_spike_desc: "Jednodniowy, wielokrotny wzrost wolumenu obrotu przy typowej zmianie ceny.",
        gap_reversal_desc: "Otwarcie daleko od poprzedniego zamknięcia, po którym cena w ciągu sesji wraca do poprzedniego poziomu.",
        drift_desc: "Pięć kolejnych sesji z umiarkowanym ruchem ceny w tym samym kierunku; żadna sesja osobno nie jest skrajna.",
        volatility_burst_desc: "Pięć kolejnych sesji o podwyższonej zmienności i szerszym zakresie cen."
      },
      metrics: {
        precisionDesc: "Jaka część zgłoszonych alarmów to rzeczywiste anomalie.",
        recallDesc: "Jaka część rzeczywistych anomalii została wykryta.",
        f1Desc: "Średnia harmoniczna precyzji i pełności.",
        defaultDesc: "Wartość miary porównawczej modeli."
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
      priceTitle: "Notowania, anomalie i sygnały",
      indicatorsTitle: "Wskaźniki techniczne",
      closePrice: "Cena zamknięcia",
      anomaly: "Anomalia",
      buySignal: "Sygnał kupna",
      sellSignal: "Sygnał sprzedaży",
      noData: "Brak danych do wyświetlenia",
      price: "Cena",
      signalLine: "Linia sygnału",
      bollingerTitle: "Wstęgi Bollingera i EMA",
      volatilityTitle: "Zmienność (ATR i odch. std.)",
      bbUpper: "Górna wstęga",
      bbLower: "Dolna wstęga",
    },
    assessment: {
      title: "Ocena modelu językowego",
      sentiment: "Sentyment",
      recommendation: "Rekomendacja",
      confidence: "Pewność",
      summary: "Podsumowanie analizy",
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
      title: "Wyniki analizy",
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
      searchButton: "Search and analyze",
      analyzing: "Analyzing...",
      exportCSV: "Export CSV",
      exportPDF: "Download PDF report",
      downloadReport: "Download results",
      processing: "Processing market data and generating the assessment...",
      selectPrompt: "Search for an instrument symbol to begin the analysis.",
      notFound: "No data found for symbol",
      error: "An error occurred",
      providerError: "The market data provider is temporarily unavailable. Please try again shortly.",
      exportError: "Failed to generate the download file.",
      subtitle: "Anomaly detection in stock market data with language model interpretation",
      marketSearch: "Instrument search",
      analysisContext: "Analysis Context",
    },
    benchmark: {
      tabs: {
        standardAnalysis: "Instrument analysis",
        modelsBenchmark: "Model comparison"
      },
      loading: {
        title: "Evaluating models...",
        subtitle: "Injecting synthetic anomalies and evaluating the models over successive runs.",
        walkForward: "In no look-ahead mode the models are retrained dozens of times in each run, so the evaluation may take up to ~20 seconds (up to ~30 seconds for 2–5 years of data)."
      },
      empty: {
        title: "Model performance comparison",
        desc: "Synthetic anomalies with known positions are injected into the quotes of the analyzed instrument, and each of the five models is checked for how well it detects them. The result helps choose the model best suited to the given instrument.",
        button: "Run model comparison"
      },
      header: {
        title: "Model performance comparison",
        subtitle: "Precision, recall and F1 score on data with synthetic anomalies.",
        barChart: "Bar chart",
        radarChart: "Radar chart",
        metricF1: "F1 score",
        metricPrecision: "Precision",
        metricRecall: "Recall",
        csv: "Export CSV",
        runsInfo: "Results are mean ± standard deviation over {n} runs with differently placed anomalies."
      },
      insights: {
        title: "Summary of results",
        mainStart: "By the selected metric",
        mainMiddle: ", the best result was achieved by",
        mainValue: "with a value of",
        mainEnd: "for the analyzed instrument.",
        precisionWinner: "Highest precision (fewest false alarms):",
        recallWinner: "Highest recall (fewest missed anomalies):",
        tradeoffTitle: "Trade-off between precision and recall",
        tradeoffDesc: "Increasing recall usually lowers precision: a model that detects more anomalies also raises more false alarms. The F1 score, the harmonic mean of both measures, makes it possible to compare models taking both aspects into account."
      },
      table: {
        model: "Model",
        precision: "Precision",
        recall: "Recall",
        f1Score: "F1 score",
        confusionMatrix: "Confusion matrix",
        actions: "Actions",
        leader: "BEST",
        tp: "TP",
        fp: "FP",
        tn: "TN",
        fn: "FN",
        selectModel: "Analyze with this model",
        selectModelTitle: "Go to the analysis tab and run the analysis with model:",
        calcError: "Calculation error:",
        tooltipTp: "True positives (correctly detected anomalies)",
        tooltipFp: "False positives (false alarms)",
        tooltipTn: "True negatives (correctly recognized typical sessions)",
        tooltipFn: "False negatives (missed anomalies)"
      },
      models: {
        isolation_forest_name: "Isolation Forest",
        isolation_forest_meta: "Isolates observations with random partitions of the feature space; effective for large, single price changes.",
        lof_name: "Local Outlier Factor",
        lof_meta: "Compares the local density of an observation with its neighbourhood; detects sessions that are unusual against a period of similar volatility. Default model.",
        ocsvm_name: "One-Class SVM",
        ocsvm_meta: "Fits a nonlinear boundary around typical observations; sensitive to parameter choice.",
        autoencoder_name: "Autoencoder (PyTorch)",
        autoencoder_meta: "A neural network that reconstructs session features; sessions with a large reconstruction error are treated as anomalies.",
        ensemble_name: "Ensemble (all models)",
        ensemble_meta: "Averages the normalized scores of the four models; reduces the risk of missing a particular type of anomaly, but dilutes the signal of the best of them."
      },
      scenario: {
        title: "Anomaly scenario",
        basic: "Basic",
        extended: "Extended",
        basicDesc: "Single, large changes in price or volume (about 3 standard deviations of the price level over the whole period). Easy to detect.",
        extendedDesc: "Anomalies scaled to the instrument's daily volatility, including multi-session ones: price drift, volatility burst, gap with reversal. Harder and closer to real events."
      },
      byType: {
        title: "Detection rate by anomaly type",
        desc: "Share of injected events of a given type detected by the model (a multi-session event counts as detected if the model flagged at least one of its sessions). Hover over a header to see the type description.",
        events: "events across all runs"
      },
      types: {
        price_spike: "Price spike",
        price_drop: "Price drop",
        volume_spike: "Volume spike",
        gap_reversal: "Gap with reversal",
        drift: "Drift",
        volatility_burst: "Volatility burst",
        price_spike_desc: "A sudden one-day rise in the closing price.",
        price_drop_desc: "A sudden one-day fall in the closing price.",
        volume_spike_desc: "A one-day multi-fold increase in trading volume with a typical price change.",
        gap_reversal_desc: "The session opens far from the previous close, after which the price returns to its previous level during the session.",
        drift_desc: "Five consecutive sessions with a moderate price move in the same direction; no single session is extreme on its own.",
        volatility_burst_desc: "Five consecutive sessions with elevated volatility and a wider price range."
      },
      metrics: {
        precisionDesc: "What share of raised alarms are actual anomalies.",
        recallDesc: "What share of actual anomalies were detected.",
        f1Desc: "Harmonic mean of precision and recall.",
        defaultDesc: "Value of the model comparison metric."
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
      priceTitle: "Quotes, anomalies and signals",
      indicatorsTitle: "Technical indicators",
      closePrice: "Closing price",
      anomaly: "Anomaly",
      buySignal: "Buy signal",
      sellSignal: "Sell signal",
      noData: "No data to display",
      price: "Price",
      signalLine: "Signal",
      bollingerTitle: "Bollinger Bands & EMA",
      volatilityTitle: "Volatility (ATR & StdDev)",
      bbUpper: "BB Upper",
      bbLower: "BB Lower",
    },
    assessment: {
      title: "Language model assessment",
      sentiment: "Sentiment",
      recommendation: "Recommendation",
      confidence: "Confidence",
      summary: "Analysis summary",
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
      title: "Analysis results",
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
