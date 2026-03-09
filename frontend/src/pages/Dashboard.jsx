import React, { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import StockChart from '../components/StockChart';
import TechnicalCharts from '../components/TechnicalCharts';
import TickerSearch from '../components/TickerSearch';
import AssessmentPanel from '../components/AssessmentPanel';
import { analyzeData, fetchMarketData } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

const Dashboard = () => {
    const { t, language } = useLanguage();
    // Stan wyszukiwania tickera
    const [searchLoading, setSearchLoading] = useState(false);
    const [tickerInfo, setTickerInfo] = useState(null);

    // Ponowna analiza po zmianie języka (jeśli dane są załadowane)
    useEffect(() => {
        if (analysisResults && (tickerInfo || processedData)) {
            runAnalysis();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [language]);

    // Stan danych i wyników analizy
    const [processedData, setProcessedData] = useState(null); // From CSV Upload
    const [analysisResults, setAnalysisResults] = useState(null);
    const [assessment, setAssessment] = useState(null);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);

    // Funkcje obsługi zdarzeń (Handlery)
    const handleUploadSuccess = (data) => {
        console.log("Upload result:", data);
        setProcessedData(data);
        setAnalysisResults(null); 
        setAssessment(null);
        setTickerInfo(null); // Clear ticker info on CSV upload
    };

    const handleSearch = async (symbol) => {
        setSearchLoading(true);
        setAnalysisResults(null);
        setAssessment(null);
        setProcessedData(null);
        setTickerInfo(null);
        
        try {
            const data = await fetchMarketData(symbol);
            setTickerInfo(data.info);
            
            // Automatyczne wyzwolenie analizy po pobraniu danych rynkowych
            await runAnalysis(data.data, data.info);
            
        } catch (err) {
            console.error(err);
            alert("Failed to fetch data for " + symbol);
        } finally {
            setSearchLoading(false);
        }
    };

    const runAnalysis = async (dataPoints = null, tickerInfoOverride = null) => {
        // Określenie źródła danych: przekazany argument lub podgląd z CSV
        const points = dataPoints || (processedData && processedData.preview);
        const info = tickerInfoOverride || tickerInfo;

        if (!points) return;
        
        setLoadingAnalysis(true);
        try {
            // Wywołanie API analizy anomalii i interpretacji AI
            const results = await analyzeData(points, 'isolation_forest', 0.05, info, language);
            
            // Aktualizacja stanu wynikami z backendu
            setAnalysisResults(results.results);
            setAssessment(results.assessment);
            
        } catch (err) {
            console.error("Analysis failed:", err);
            alert("Analysis failed check console.");
        } finally {
            setLoadingAnalysis(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <header className="mb-8 text-center">
                <h1 className="text-4xl font-bold text-blue-400 mb-2">StockGuard AI</h1>
                <p className="text-gray-400">Advanced Anomaly Detection & AI Interpretation</p>
            </header>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                {/* Lewa kolumna: Metody wprowadzania danych */}
                <div className="space-y-6">
                     <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
                        <h2 className="text-xl font-bold mb-4 text-purple-400">{t('dashboard.searchButton')}</h2>
                        <TickerSearch onSearch={handleSearch} loading={searchLoading} />
                        
                        <div className="relative flex py-2 items-center">
                            <div className="flex-grow border-t border-gray-600"></div>
                            <span className="flex-shrink-0 mx-4 text-gray-400 font-medium">{t('dashboard.or')}</span>
                            <div className="flex-grow border-t border-gray-600"></div>
                        </div>

                        <h2 className="text-xl font-bold mb-4 text-blue-400">{t('dashboard.uploadTitle')}</h2>
                        <FileUpload onUploadSuccess={handleUploadSuccess} />
                    </div>
                </div>

                {/* Prawa kolumna: Kontekst i informacje */}
                 <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
                    <h2 className="text-xl font-bold mb-4 text-gray-300">Analysis Context</h2>
                    
                    {tickerInfo && (
                        <div className="mb-4 p-4 bg-slate-700/50 rounded border border-slate-600">
                            <h3 className="text-lg font-bold text-blue-300">{tickerInfo.name} ({tickerInfo.symbol})</h3>
                            <p className="text-sm text-gray-400">{tickerInfo.sector} - {tickerInfo.industry}</p>
                            {/* Display full description logic with toggle could be added, but for now full description as requested */}
                            <p className="mt-2 text-gray-300 text-sm leading-relaxed max-h-[300px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-500 pr-2">
                                {tickerInfo.description}
                            </p>
                        </div>
                    )}

                    {processedData && !tickerInfo && (
                        <div className="mb-4">
                            <p className="text-green-400 font-semibold">{t('dashboard.customFile')}</p>
                            <p className="text-gray-300">{t('dashboard.filename')}: {processedData.filename}</p>
                            <p className="text-gray-300">{t('dashboard.rows')}: {processedData.total_rows}</p>
                        </div>
                    )}
                    
                    {!processedData && !tickerInfo && !searchLoading && (
                        <div className="flex items-center justify-center h-32 text-gray-500 italic border-2 border-dashed border-gray-700 rounded">
                            {t('dashboard.selectPrompt')}
                        </div>
                    )}

                    {/* Ręczne wyzwolenie analizy dla danych z CSV */}
                    {processedData && !tickerInfo && (
                        <button 
                            onClick={() => runAnalysis()}
                            disabled={loadingAnalysis}
                            className="mt-4 w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 transition-colors"
                        >
                            {loadingAnalysis ? t('dashboard.runningAnalysis') : t('dashboard.manualTrigger')}
                        </button>
                    )}
                    
                    {loadingAnalysis && (
                        <div className="mt-4 p-3 bg-blue-900/20 text-blue-400 rounded text-center animate-pulse">
                            {t('dashboard.processing')}
                        </div>
                    )}
                 </div>
            </div>

            {/* AI Assessment Panel */}
             {assessment && (
                <div className="mb-8 animate-fade-in-up">
                    <AssessmentPanel assessment={assessment} />
                </div>
             )}

            {/* Wizualizacja wyników */}
            {analysisResults && (
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
        </div>
    );
};

export default Dashboard;
