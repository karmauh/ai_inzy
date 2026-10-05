import { useState, useEffect } from 'react';
import StockChart from '../components/StockChart';
import TechnicalCharts from '../components/TechnicalCharts';
import TickerSearch from '../components/TickerSearch';
import AssessmentPanel from '../components/AssessmentPanel';
import ModelBenchmark from '../components/ModelBenchmark';
import AnalysisSettings from '../components/AnalysisSettings';
import ResultsTable from '../components/ResultsTable';
import { analyzeData, fetchMarketData, exportCSV, exportPDF, evaluateModelsAPI, generateAssessment } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

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
    
    // Ustawienia analizy (panel "Ustawienia analizy"); zachowywane między wyszukiwaniami
    const [symbol, setSymbol] = useState(null);
    const [period, setPeriod] = useState('1y');
    const [currentModel, setCurrentModel] = useState('isolation_forest');
    // Czułość = odsetek sesji oznaczanych jako anomalie (contamination); używana też jako frakcja anomalii w benchmarku
    const [contamination, setContamination] = useState(0.05);
    // Tryb detekcji: 'batch' (analiza historyczna) lub 'walk_forward' (bez wglądu w przyszłość)
    const [detectionMode, setDetectionMode] = useState('batch');

    // Po zmianie języka generujemy tylko brakującą ocenę AI (bez ponownego uruchamiania modelu ML)
    useEffect(() => {
        if (!analysisResults || assessments[language] || loadingAnalysis) return;

        let cancelled = false;
        setLoadingAnalysis(true);
        generateAssessment(analysisResults, tickerInfo, language)
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
            handleExport(() => exportPDF(analysisResults, assessment, tickerInfo, language));
        }
    };

    const handleSearch = async (newSymbol, periodToUse = period) => {
        setSearchLoading(true);
        setAnalysisResults(null);
        setAssessments({});
        setBenchmarkData(null);
        setActiveTab('analysis');
        setTickerInfo(null);
        setError(null);
        
        try {
            const data = await fetchMarketData(newSymbol, periodToUse);
            setSymbol(newSymbol);
            setTickerInfo(data.info);
            
            // Automatyczne wyzwolenie analizy po pobraniu danych rynkowych
            await runAnalysis({ points: data.data, info: data.info });
            
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

    // Nadpisania pozwalają użyć nowej wartości ustawienia, zanim stan Reacta zostanie zaktualizowany
    const runAnalysis = async ({
        points = analysisResults,
        info = tickerInfo,
        model = currentModel,
        mode = detectionMode,
        sensitivity = contamination,
    } = {}) => {
        if (!points) return;
        
        setLoadingAnalysis(true);
        setError(null);
        try {
            // Wywołanie API analizy anomalii i interpretacji AI
            const results = await analyzeData(points, model, sensitivity, info, language, mode);
            
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

    const handleModeChange = (mode) => {
        if (mode === detectionMode || loadingAnalysis) return;
        setDetectionMode(mode);
        // Benchmark dotyczył poprzedniego trybu – zostanie policzony ponownie na żądanie
        setBenchmarkData(null);
        runAnalysis({ mode });
    };

    const handleModelChange = (model) => {
        if (model === currentModel || loadingAnalysis) return;
        setCurrentModel(model);
        runAnalysis({ model });
    };

    const handleContaminationChange = (sensitivity) => {
        if (sensitivity === contamination || loadingAnalysis) return;
        setContamination(sensitivity);
        // Benchmark wstrzykuje tyle anomalii, ile wynosi czułość – wyniki dla starej wartości są nieaktualne
        setBenchmarkData(null);
        runAnalysis({ sensitivity });
    };

    const handlePeriodChange = (newPeriod) => {
        if (newPeriod === period || loadingAnalysis || searchLoading) return;
        setPeriod(newPeriod);
        // Inny okres to inne dane – pobieramy je ponownie (przed pierwszym wyszukiwaniem tylko zapamiętujemy wybór)
        if (symbol) handleSearch(symbol, newPeriod);
    };

    const handleRunBenchmark = async (scenario = benchmarkScenario) => {
        setActiveTab('benchmark');
        if (benchmarkData?.metadata?.scenario === scenario) return; // Unikamy podwójnego żądania
        
        setLoadingBenchmark(true);
        try {
            const results = await evaluateModelsAPI(analysisResults, contamination, undefined, detectionMode, scenario);
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
                            <TickerSearch onSearch={handleSearch} loading={searchLoading} />
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
                                        <span className="text-lg group-hover:scale-110 transition-transform">📄</span> {t('dashboard.exportPDF')}
                                    </button>
                                    <button
                                        onClick={handleExportCSV}
                                        className="w-full bg-primary-600/20 hover:bg-primary-600/30 text-primary-400 border border-primary-600/50 font-bold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group shadow-sm"
                                    >
                                        <span className="text-lg group-hover:scale-110 transition-transform">📊</span> {t('dashboard.exportCSV')}
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

            <AnalysisSettings
                model={currentModel}
                period={period}
                contamination={contamination}
                mode={detectionMode}
                disabled={loadingAnalysis || searchLoading}
                onModelChange={handleModelChange}
                onPeriodChange={handlePeriodChange}
                onContaminationChange={handleContaminationChange}
                onModeChange={handleModeChange}
            />

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
                     {/* Główny wykres giełdowy */}
                     <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
                        <StockChart data={analysisResults} />
                     </div>

                     {/* Siatka wykresów wskaźników technicznych */}
                     <TechnicalCharts data={analysisResults} />

                     {/* Sekcja tabeli wyników */}
                     <ResultsTable rows={analysisResults} />
                </div>
            )}
            {/* Widok Benchmarku */}
            {activeTab === 'benchmark' && (
                <ModelBenchmark
                    evaluationData={benchmarkData?.evaluation}
                    detectionMode={detectionMode}
                    scenario={benchmarkScenario}
                    onScenarioChange={handleScenarioChange}
                    nRuns={benchmarkData?.metadata?.n_runs}
                    loading={loadingBenchmark}
                    onRunBenchmark={() => handleRunBenchmark()}
                    onSelectModel={(modelKey) => {
                        setActiveTab('analysis');
                        handleModelChange(modelKey);
                    }}
                />
            )}
        </div>
    );
};

export default Dashboard;
