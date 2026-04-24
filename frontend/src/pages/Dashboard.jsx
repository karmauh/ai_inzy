import React, { useState, useEffect } from 'react';
import StockChart from '../components/StockChart';
import TechnicalCharts from '../components/TechnicalCharts';
import TickerSearch from '../components/TickerSearch';
import AssessmentPanel from '../components/AssessmentPanel';
import ModelBenchmark from '../components/ModelBenchmark';
import { analyzeData, fetchMarketData, exportCSV, exportPDF, evaluateModelsAPI } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

const Dashboard = () => {
    const { t, language } = useLanguage();
    // Stan wyszukiwania tickera
    const [searchLoading, setSearchLoading] = useState(false);
    const [tickerInfo, setTickerInfo] = useState(null);
    const [error, setError] = useState(null);

    // Ponowna analiza po zmianie języka (jeśli dane są załadowane)
    useEffect(() => {
        if (analysisResults && tickerInfo) {
            runAnalysis();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [language]);

    // Stan danych i wyników analizy
    const [analysisResults, setAnalysisResults] = useState(null);
    const [assessment, setAssessment] = useState(null);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);
    
    // Stany dla Benchmarku Modeli
    const [activeTab, setActiveTab] = useState('analysis');
    const [benchmarkData, setBenchmarkData] = useState(null);
    const [loadingBenchmark, setLoadingBenchmark] = useState(false);
    
    // Stan wyboru aktualnego modelu (powiązanie z Benchmarkiem)
    const [currentModel, setCurrentModel] = useState('isolation_forest');

    // Obsługa eksportu
    const handleExportCSV = () => {
        if (analysisResults) exportCSV(analysisResults);
    };

    const handleExportPDF = () => {
        if (analysisResults && assessment && tickerInfo) {
            exportPDF(analysisResults, assessment, tickerInfo, language);
        }
    };

    const handleSearch = async (symbol) => {
        setSearchLoading(true);
        setAnalysisResults(null);
        setAssessment(null);
        setBenchmarkData(null);
        setActiveTab('analysis');
        setCurrentModel('isolation_forest');
        setTickerInfo(null);
        setError(null);
        
        try {
            const data = await fetchMarketData(symbol);
            setTickerInfo(data.info);
            
            // Automatyczne wyzwolenie analizy po pobraniu danych rynkowych
            await runAnalysis(data.data, data.info);
            
        } catch (err) {
            console.error(err);
            if (err.response?.status === 404) {
                setError(`${t('dashboard.notFound')} ${symbol.toUpperCase()}`);
            } else {
                setError(t('dashboard.error') || "Wystąpił błąd");
            }
        } finally {
            setSearchLoading(false);
        }
    };

    const runAnalysis = async (dataPoints = null, tickerInfoOverride = null, modelOverride = null) => {
        // Określenie źródła danych: przekazany argument lub aktualne wyniki analizy
        const points = dataPoints || analysisResults;
        const info = tickerInfoOverride || tickerInfo;
        const modelToUse = modelOverride || currentModel;

        if (!points) return;
        
        setLoadingAnalysis(true);
        try {
            // Wywołanie API analizy anomalii i interpretacji AI
            const results = await analyzeData(points, modelToUse, 0.05, info, language);
            
            // Aktualizacja stanu wynikami z backendu
            setAnalysisResults(results.results);
            setAssessment(results.assessment);
            if (modelOverride) setCurrentModel(modelOverride);
            
        } catch (err) {
            console.error("Analysis failed:", err);
            setError(t('dashboard.error') || "Wystąpił błąd");
        } finally {
            setLoadingAnalysis(false);
        }
    };

    const handleRunBenchmark = async () => {
        setActiveTab('benchmark');
        if (benchmarkData) return; // Unikamy podwójnego żądania
        
        setLoadingBenchmark(true);
        try {
            const results = await evaluateModelsAPI(analysisResults);
            setBenchmarkData(results);
        } catch (err) {
            console.error("Benchmark failed:", err);
            setError(t('dashboard.error') || "Wystąpił błąd podczas pobierania benchmarku");
        } finally {
            setLoadingBenchmark(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <header className="mb-8 text-center">
                <h1 className="text-4xl font-bold text-blue-400 mb-2">StockGuard AI</h1>
                <p className="text-gray-400">Advanced Anomaly Detection & AI Interpretation</p>
            </header>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                {/* Kolumna: Wyszukiwanie i Akcje */}
                <div className="space-y-6">
                    <div className="bg-slate-800 p-6 rounded-xl shadow-2xl border border-slate-700/50 flex flex-col h-full">
                        <div className="mb-6 border-b border-slate-700/50 pb-4">
                            <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
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
                            <div className="mt-8 pt-6 border-t border-slate-700/50">
                                <h2 className="text-sm font-semibold mb-4 text-gray-400 uppercase tracking-wider">{t('dashboard.downloadReport')}</h2>
                                <div className="grid grid-cols-1 gap-3">
                                    <button 
                                        onClick={handleExportPDF}
                                        className="w-full bg-red-600/10 hover:bg-red-600/20 text-red-500 border border-red-900/50 font-bold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group shadow-sm"
                                    >
                                        <span className="text-lg group-hover:scale-110 transition-transform">📄</span> {t('dashboard.exportPDF')}
                                    </button>
                                    <button 
                                        onClick={handleExportCSV}
                                        className="w-full bg-green-600/10 hover:bg-green-600/20 text-green-500 border border-green-900/50 font-bold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group shadow-sm"
                                    >
                                        <span className="text-lg group-hover:scale-110 transition-transform">📊</span> {t('dashboard.exportCSV')}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Kolumna: Kontekst i informacje */}
                 <div className="lg:col-span-2 bg-slate-800 p-6 rounded-xl shadow-2xl border border-slate-700/50 flex flex-col h-full">
                    <div className="mb-6 border-b border-slate-700/50 pb-4">
                        <h2 className="text-xl font-bold text-gray-100">Analysis Context</h2>
                    </div>
                    
                    <div className="flex-1 flex flex-col">
                        {tickerInfo ? (
                            <div className="flex-1 flex flex-col">
                                <div className="p-5 bg-slate-900/50 rounded-xl border border-slate-700/50 backdrop-blur-sm h-full shadow-inner">
                                    <div className="flex flex-col sm:flex-row justify-between items-start mb-4 gap-4">
                                        <div>
                                            <h3 className="text-2xl font-black text-blue-400 leading-none mb-1">{tickerInfo.symbol}</h3>
                                            <p className="text-base font-semibold text-gray-200">{tickerInfo.name}</p>
                                        </div>
                                        <div className="bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full text-xs font-bold border border-blue-500/20 uppercase">
                                            {tickerInfo.sector}
                                        </div>
                                    </div>
                                    <div className="h-px bg-slate-700/50 w-full mb-4" />
                                    <p className="text-gray-300 text-sm leading-relaxed max-h-[250px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent pr-3 font-light">
                                        {tickerInfo.description}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            !searchLoading && (
                                <div className="flex flex-col items-center justify-center flex-1 min-h-[200px] text-gray-500 italic border-2 border-dashed border-slate-700/50 rounded-xl bg-slate-900/20 p-8 text-center gap-4">
                                    <div className="text-4xl opacity-20">🔎</div>
                                    <p className="max-w-xs">{t('dashboard.selectPrompt')}</p>
                                </div>
                            )
                        )}
                        
                        {loadingAnalysis && (
                            <div className="mt-6 p-4 bg-blue-600/10 text-blue-400 rounded-xl text-center animate-pulse border border-blue-500/20 flex items-center justify-center gap-3 shadow-lg backdrop-blur-sm">
                                <div className="animate-bounce text-xl">🚀</div>
                                <span className="font-semibold tracking-wide text-sm">{t('dashboard.processing')}</span>
                            </div>
                        )}
                    </div>
                 </div>
            </div>

            {/* Widoki zakładek */}
            {analysisResults && (
                <div className="mb-6 flex space-x-2 bg-slate-800 p-1.5 rounded-xl w-fit mx-auto border border-slate-700/50 shadow-lg animate-fade-in-up">
                    <button
                        onClick={() => setActiveTab('analysis')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-bold tracking-wide transition-all ${activeTab === 'analysis' ? 'bg-blue-600 text-white shadow-md' : 'text-gray-400 hover:text-gray-200 hover:bg-slate-700/50'}`}
                    >
                        {t('benchmark.tabs.standardAnalysis')}
                    </button>
                    <button
                        onClick={() => setActiveTab('benchmark')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-bold tracking-wide transition-all ${activeTab === 'benchmark' ? 'bg-purple-600 text-white shadow-md' : 'text-gray-400 hover:text-gray-200 hover:bg-slate-700/50'}`}
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
                     <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
                        <StockChart data={analysisResults} />
                     </div>
                     
                     {/* Siatka wykresów wskaźników technicznych */}
                     <TechnicalCharts data={analysisResults} />

                     {/* Sekcja tabeli wyników */}
                     <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
                         <h2 className="text-xl font-bold mb-4 text-blue-400">{t('table.title')}</h2>
                         <div className="overflow-x-auto max-h-[400px] scrollbar-thin scrollbar-thumb-slate-600">
                            <table className="w-full text-left text-gray-300">
                                <thead className="bg-slate-700/50 sticky top-0">
                                    <tr className="border-b border-gray-700">
                                        <th className="py-3 px-4">{t('table.date')}</th>
                                        <th className="py-3 px-4">{t('table.close')}</th>
                                        <th className="py-3 px-4">{t('table.features')}</th>
                                        <th className="py-3 px-4">{t('table.status')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {analysisResults.map((row, idx) => (
                                        <tr key={idx} className={`border-b border-gray-700 hover:bg-slate-700/50 transition-colors ${row.is_anomaly ? 'bg-red-900/20' : ''}`}>
                                            <td className="py-2 px-4">{row.date}</td>
                                            <td className="py-2 px-4">{typeof row.close === 'number' ? row.close.toFixed(2) : row.close}</td>
                                            <td className="py-2 px-4">{row.anomaly_score.toFixed(4)}</td>
                                            <td className="py-2 px-4">
                                                {row.is_anomaly ? (
                                                    <span className="text-red-400 font-bold flex items-center gap-1">
                                                        ⚠️ {t('table.anomaly')}
                                                    </span>
                                                ) : (
                                                    <span className="text-green-400 text-sm">{t('table.normal')}</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                         </div>
                     </div>
                </div>
            )}
            {/* Widok Benchmarku */}
            {activeTab === 'benchmark' && (
                <ModelBenchmark 
                    evaluationData={benchmarkData?.evaluation}
                    loading={loadingBenchmark}
                    onRunBenchmark={handleRunBenchmark}
                    onSelectModel={(modelKey) => {
                        setActiveTab('analysis');
                        runAnalysis(null, null, modelKey);
                    }}
                />
            )}
        </div>
    );
};

export default Dashboard;
