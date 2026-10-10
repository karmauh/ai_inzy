import { useState, useEffect, lazy, Suspense } from 'react';
import TickerSearch from '../components/TickerSearch';
import AssessmentPanel from '../components/AssessmentPanel';
import AnalysisSettings from '../components/AnalysisSettings';
import ResultsTable from '../components/ResultsTable';
import { analyzeData, fetchMarketData, exportCSV, exportPDF, evaluateModelsAPI, generateAssessment } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

// Wykresy i benchmark korzystają z biblioteki Recharts (największa część paczki JS) – ładujemy je dopiero,
// gdy są potrzebne, dzięki czemu ekran startowy (wyszukiwarka) wczytuje się szybciej
const StockChart = lazy(() => import('../components/StockChart'));
const TechnicalCharts = lazy(() => import('../components/TechnicalCharts'));
const ModelBenchmark = lazy(() => import('../components/ModelBenchmark'));

const ChartFallback = () => (
    <div className="h-[200px] flex items-center justify-center text-neutral-500 text-sm animate-pulse">…</div>
);

const DEFAULT_SETTINGS = { model: 'lof', period: '1y', contamination: 0.05, mode: 'batch' };
const SETTINGS_KEYS = Object.keys(DEFAULT_SETTINGS);

const Dashboard = () => {
    const { t, language } = useLanguage();
    // Stan wyszukiwania tickera
    const [searchLoading, setSearchLoading] = useState(false);
    const [tickerInfo, setTickerInfo] = useState(null);
    const [error, setError] = useState(null);

    // Stan danych i wyników analizy; oceny AI trzymane per język, by zmiana języka nie wymagała ponownej analizy
    const [analysisResults, setAnalysisResults] = useState(null);
    const [assessments, setAssessments] = useState({});
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);
    const assessment = assessments[language] || null;
    
    // Stany dla Benchmarku Modeli
    const [activeTab, setActiveTab] = useState('analysis');
    const [benchmarkData, setBenchmarkData] = useState(null);
    const [loadingBenchmark, setLoadingBenchmark] = useState(false);
    // Scenariusz benchmarku: 'basic' (duże, pojedyncze anomalie) lub 'extended' (realistyczne, także wielosesyjne)
    const [benchmarkScenario, setBenchmarkScenario] = useState('basic');
    
    // Ustawienia analizy: 'settings' to ustawienia, na których powstały widoczne wyniki,
    // 'draft' to wartości w panelu – stosowane dopiero przyciskiem "Zastosuj" lub przy wyszukiwaniu.
    // contamination = czułość (odsetek sesji oznaczanych jako anomalie), używana też jako frakcja anomalii w benchmarku;
    // mode: 'batch' (analiza historyczna) lub 'walk_forward' (bez wglądu w przyszłość)
    const [settings, setSettings] = useState(DEFAULT_SETTINGS);
    const [draft, setDraft] = useState(DEFAULT_SETTINGS);
    const [showSettings, setShowSettings] = useState(false);
    const [symbol, setSymbol] = useState(null);
    const settingsDirty = SETTINGS_KEYS.some((key) => draft[key] !== settings[key]);

    // Po zmianie języka generujemy tylko brakującą ocenę AI (bez ponownego uruchamiania modelu ML)
    useEffect(() => {
        if (!analysisResults || assessments[language] || loadingAnalysis) return;

        let cancelled = false;
        setLoadingAnalysis(true);
        generateAssessment(analysisResults, tickerInfo, language, settings)
            .then((result) => {
                if (!cancelled) setAssessments((prev) => ({ ...prev, [language]: result }));
            })
            .catch((err) => {
                console.error('Assessment failed:', err);
                if (!cancelled) setError(t('dashboard.error'));
            })
            .finally(() => {
                if (!cancelled) setLoadingAnalysis(false);
            });

        return () => { cancelled = true; };
        // Reagujemy wyłącznie na zmianę języka; pozostałe wartości są odczytywane w momencie zmiany
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [language]);

    // Obsługa eksportu
    const handleExport = async (exportFn) => {
        try {
            await exportFn();
        } catch (err) {
            console.error('Export failed:', err);
            setError(t('dashboard.exportError'));
        }
    };

    const handleExportCSV = () => {
        if (analysisResults) handleExport(() => exportCSV(analysisResults));
    };

    const handleExportPDF = () => {
        if (analysisResults && assessment && tickerInfo) {
            handleExport(() => exportPDF(analysisResults, assessment, tickerInfo, language, settings));
        }
    };

    // Wyszukiwanie zawsze używa ustawień widocznych w panelu (szkicu) – stają się one ustawieniami zastosowanymi
    const handleSearch = async (newSymbol) => {
        const applied = draft;
        setSettings(applied);
        setSearchLoading(true);
        setAnalysisResults(null);
        setAssessments({});
        setBenchmarkData(null);
        setActiveTab('analysis');
        setTickerInfo(null);
        setError(null);
        
        try {
            const data = await fetchMarketData(newSymbol, applied.period);
            setSymbol(newSymbol);
            setTickerInfo(data.info);
            
            // Automatyczne wyzwolenie analizy po pobraniu danych rynkowych
            await runAnalysis({ points: data.data, info: data.info, analysisSettings: applied });
            
        } catch (err) {
            console.error(err);
            if (err.response?.status === 404) {
                setError(`${t('dashboard.notFound')} ${newSymbol.toUpperCase()}`);
            } else if (err.response?.status === 502) {
                setError(t('dashboard.providerError'));
            } else {
                setError(t('dashboard.error'));
            }
        } finally {
            setSearchLoading(false);
        }
    };

    // Nadpisania pozwalają użyć nowych wartości, zanim stan Reacta zostanie zaktualizowany
    const runAnalysis = async ({ points = analysisResults, info = tickerInfo, analysisSettings = settings } = {}) => {
        if (!points) return;
        
        setLoadingAnalysis(true);
        setError(null);
        try {
            // Wywołanie API analizy anomalii i interpretacji AI
            const { model, contamination, mode } = analysisSettings;
            const results = await analyzeData(points, model, contamination, info, language, mode);
            
            // Aktualizacja stanu wynikami z backendu
            setAnalysisResults(results.results);
            setAssessments({ [language]: results.assessment });
            
        } catch (err) {
            console.error("Analysis failed:", err);
            setError(t('dashboard.error'));
        } finally {
            setLoadingAnalysis(false);
        }
    };

    const handleScenarioChange = (scenario) => {
        if (scenario === benchmarkScenario || loadingBenchmark) return;
        setBenchmarkScenario(scenario);
        // Wyniki są już widoczne – przeliczamy od razu; w pustym widoku tylko zmieniamy wybór
        if (benchmarkData) {
            setBenchmarkData(null);
            handleRunBenchmark(scenario);
        }
    };

    // "Zastosuj ustawienia": jedna analiza ze wszystkimi zmianami naraz; nowy okres wymaga ponownego pobrania danych
    const handleApplySettings = () => {
        if (!settingsDirty || !symbol || loadingAnalysis || searchLoading) return;
        if (draft.period !== settings.period) {
            handleSearch(symbol);
            return;
        }
        // Benchmark obejmuje wszystkie modele, ale zależy od trybu i czułości
        if (draft.mode !== settings.mode || draft.contamination !== settings.contamination) setBenchmarkData(null);
        setSettings(draft);
        runAnalysis({ analysisSettings: draft });
    };

    const handleResetSettings = () => setDraft(settings);

    // "Analizuj tym modelem" w benchmarku działa od razu (świadoma, pojedyncza decyzja) i aktualizuje panel
    const handleSelectModelFromBenchmark = (model) => {
        setActiveTab('analysis');
        if (model === settings.model || loadingAnalysis) return;
        const applied = { ...settings, model };
        setSettings(applied);
        setDraft((prev) => ({ ...prev, model }));
        runAnalysis({ analysisSettings: applied });
    };

    const handleRunBenchmark = async (scenario = benchmarkScenario) => {
        setActiveTab('benchmark');
        if (benchmarkData?.metadata?.scenario === scenario) return; // Unikamy podwójnego żądania
        
        setLoadingBenchmark(true);
        try {
            const results = await evaluateModelsAPI(analysisResults, settings.contamination, undefined, settings.mode, scenario);
            setBenchmarkData(results);
        } catch (err) {
            console.error("Benchmark failed:", err);
            setError(t('dashboard.error'));
        } finally {
            setLoadingBenchmark(false);
        }
    };

    return (
        <div>
            <p className="mb-8 text-center text-neutral-400">{t('dashboard.subtitle')}</p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                {/* Kolumna: Wyszukiwanie i Akcje */}
                <div className="space-y-6">
                    <div className="bg-neutral-800 p-6 rounded-xl shadow-2xl border border-neutral-700 flex flex-col h-full">
                        <div className="mb-6 border-b border-neutral-700 pb-4">
                            <h2 className="text-xl font-bold text-white">
                                {t('dashboard.searchButton')}
                            </h2>
                        </div>

                        <div className="flex-1">
                            <TickerSearch
                                onSearch={handleSearch}
                                loading={searchLoading}
                                settings={draft}
                                settingsOpen={showSettings}
                                settingsPending={settingsDirty && Boolean(symbol)}
                                onToggleSettings={() => setShowSettings((open) => !open)}
                            />
                            {error && (
                                <div className="mt-4 p-4 bg-red-900/50 border border-red-500/50 rounded-xl text-red-200 text-sm animate-fade-in-up">
                                    <div className="flex gap-3 items-center">
                                        <span className="text-xl">⚠️</span>
                                        <strong>{error}</strong>
                                    </div>
                                </div>
                            )}
                        </div>

                        {analysisResults && (
                            <div className="mt-8 pt-6 border-t border-neutral-700">
                                <h2 className="text-sm font-semibold mb-4 text-neutral-400 uppercase tracking-wider">{t('dashboard.downloadReport')}</h2>
                                <div className="grid grid-cols-1 gap-3">
                                    <button
                                        onClick={handleExportPDF}
                                        className="w-full bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-600/50 font-bold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group shadow-sm"
                                    >
                                        {t('dashboard.exportPDF')}
                                    </button>
                                    <button
                                        onClick={handleExportCSV}
                                        className="w-full bg-primary-600/20 hover:bg-primary-600/30 text-primary-400 border border-primary-600/50 font-bold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group shadow-sm"
                                    >
                                        {t('dashboard.exportCSV')}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Kolumna: Kontekst i informacje */}
                 <div className="lg:col-span-2 bg-neutral-800 p-6 rounded-xl shadow-2xl border border-neutral-700 flex flex-col h-full">
                    <div className="mb-6 border-b border-neutral-700 pb-4">
                        <h2 className="text-xl font-bold text-white">{t('dashboard.analysisContext')}</h2>
                    </div>

                    <div className="flex-1 flex flex-col">
                        {tickerInfo ? (
                            <div className="flex-1 flex flex-col">
                                <div className="p-5 bg-neutral-700/50 rounded-xl border border-neutral-600 backdrop-blur-sm h-full shadow-inner">
                                    <div className="flex flex-col sm:flex-row justify-between items-start mb-4 gap-4">
                                        <div>
                                            <h3 className="text-2xl font-black text-primary-400 leading-none mb-1">{tickerInfo.symbol}</h3>
                                            <p className="text-base font-semibold text-neutral-200">{tickerInfo.name}</p>
                                        </div>
                                        {tickerInfo.sector && (
                                            <div className="bg-primary-500/20 text-primary-400 px-3 py-1 rounded-full text-xs font-bold border border-primary-500/40 uppercase">
                                                {tickerInfo.sector}
                                            </div>
                                        )}
                                    </div>
                                    <div className="h-px bg-neutral-600 w-full mb-4" />
                                    <p className="text-neutral-300 text-sm leading-relaxed max-h-[250px] overflow-y-auto scrollbar-thin scrollbar-thumb-neutral-600 scrollbar-track-transparent pr-3 font-light">
                                        {tickerInfo.description}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            !searchLoading && (
                                <div className="flex flex-col items-center justify-center flex-1 min-h-[200px] text-neutral-500 italic border-2 border-dashed border-neutral-600 rounded-xl bg-neutral-700/20 p-8 text-center gap-4">
                                    <div className="text-4xl opacity-20">🔎</div>
                                    <p className="max-w-xs">{t('dashboard.selectPrompt')}</p>
                                </div>
                            )
                        )}

                        {loadingAnalysis && (
                            <div className="mt-6 p-4 bg-primary-600/20 text-primary-400 rounded-xl text-center animate-pulse border border-primary-500/30 flex items-center justify-center gap-3 shadow-lg backdrop-blur-sm">
                                <div className="animate-bounce text-xl">🚀</div>
                                <span className="font-semibold tracking-wide text-sm">{t('dashboard.processing')}</span>
                            </div>
                        )}
                    </div>
                 </div>
            </div>

            {showSettings && (
                <AnalysisSettings
                    value={draft}
                    onChange={(changes) => setDraft((prev) => ({ ...prev, ...changes }))}
                    dirty={settingsDirty}
                    hasResults={Boolean(symbol)}
                    disabled={loadingAnalysis || searchLoading}
                    onApply={handleApplySettings}
                    onReset={handleResetSettings}
                    onClose={() => setShowSettings(false)}
                />
            )}

            {/* Widoki zakładek */}
            {analysisResults && (
                <div className="mb-6 flex space-x-2 bg-neutral-800 p-1.5 rounded-xl w-fit mx-auto border border-neutral-700 shadow-lg animate-fade-in-up">
                    <button
                        onClick={() => setActiveTab('analysis')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-bold tracking-wide transition-all ${activeTab === 'analysis' ? 'bg-primary-600 text-white shadow-md' : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-700'}`}
                    >
                        {t('benchmark.tabs.standardAnalysis')}
                    </button>
                    <button
                        onClick={() => setActiveTab('benchmark')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-bold tracking-wide transition-all ${activeTab === 'benchmark' ? 'bg-primary-600 text-white shadow-md' : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-700'}`}
                    >
                        {t('benchmark.tabs.modelsBenchmark')}
                    </button>
                </div>
            )}

            {/* AI Assessment Panel */}
             {assessment && activeTab === 'analysis' && (
                <div className="mb-8 animate-fade-in-up">
                    <AssessmentPanel assessment={assessment} />
                </div>
             )}

            {/* Wizualizacja wyników Analizy */}
            {analysisResults && activeTab === 'analysis' && (
                <div className="space-y-8 animate-fade-in-up">
                     <Suspense fallback={<ChartFallback />}>
                         {/* Główny wykres giełdowy */}
                         <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
                            <StockChart data={analysisResults} />
                         </div>

                         {/* Siatka wykresów wskaźników technicznych */}
                         <TechnicalCharts data={analysisResults} />
                     </Suspense>

                     {/* Sekcja tabeli wyników */}
                     <ResultsTable rows={analysisResults} />
                </div>
            )}
            {/* Widok Benchmarku */}
            {activeTab === 'benchmark' && (
                <Suspense fallback={<ChartFallback />}>
                <ModelBenchmark
                    evaluationData={benchmarkData?.evaluation}
                    detectionMode={settings.mode}
                    scenario={benchmarkScenario}
                    onScenarioChange={handleScenarioChange}
                    nRuns={benchmarkData?.metadata?.n_runs}
                    loading={loadingBenchmark}
                    onRunBenchmark={() => handleRunBenchmark()}
                    onSelectModel={handleSelectModelFromBenchmark}
                />
                </Suspense>
            )}
        </div>
    );
};

export default Dashboard;
