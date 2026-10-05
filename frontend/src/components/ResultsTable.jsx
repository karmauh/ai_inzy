import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import ExplanationList from './ExplanationList';

// Tabela wyników analizy z filtrem "tylko anomalie" i wyjaśnieniem, co było nietypowe w danej sesji
const ResultsTable = ({ rows }) => {
    const { t } = useLanguage();
    const [onlyAnomalies, setOnlyAnomalies] = useState(false);

    const anomalyCount = rows.filter((row) => row.is_anomaly).length;
    // Przy filtrze najnowsze anomalie na górze – zwykle to one są najciekawsze
    const visible = onlyAnomalies ? rows.filter((row) => row.is_anomaly).reverse() : rows;

    return (
        <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
                <h2 className="text-xl font-bold text-primary-400">{t('table.title')}</h2>
                <label className="flex items-center gap-2 text-sm text-neutral-300 cursor-pointer select-none">
                    <input
                        type="checkbox"
                        checked={onlyAnomalies}
                        onChange={(e) => setOnlyAnomalies(e.target.checked)}
                        className="accent-primary-500 w-4 h-4"
                    />
                    {t('table.onlyAnomalies')} ({anomalyCount})
                </label>
            </div>
            <p className="text-xs text-neutral-500 mb-4">{t('table.explanationNote')}</p>
            <div className="overflow-x-auto max-h-[480px] scrollbar-thin scrollbar-thumb-neutral-600">
                <table className="w-full text-left text-neutral-300">
                    <thead className="bg-neutral-700 sticky top-0 z-10">
                        <tr className="border-b border-neutral-600">
                            <th className="py-3 px-4 text-neutral-200 font-semibold">{t('table.date')}</th>
                            <th className="py-3 px-4 text-neutral-200 font-semibold">{t('table.close')}</th>
                            <th className="py-3 px-4 text-neutral-200 font-semibold">{t('table.score')}</th>
                            <th className="py-3 px-4 text-neutral-200 font-semibold">{t('table.status')}</th>
                            <th className="py-3 px-4 text-neutral-200 font-semibold">{t('table.why')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {visible.map((row) => (
                            <tr key={row.date} className={`border-b border-neutral-700 hover:bg-neutral-700/50 transition-colors align-top ${row.is_anomaly ? 'bg-red-900/20' : ''}`}>
                                <td className="py-2 px-4 whitespace-nowrap">{row.date}</td>
                                <td className="py-2 px-4">{typeof row.close === 'number' ? row.close.toFixed(2) : row.close}</td>
                                <td className="py-2 px-4">{typeof row.anomaly_score === 'number' ? row.anomaly_score.toFixed(4) : '—'}</td>
                                <td className="py-2 px-4 whitespace-nowrap">
                                    {row.is_anomaly ? (
                                        <span className="text-red-400 font-bold flex items-center gap-1">
                                            ⚠️ {t('table.anomaly')}
                                        </span>
                                    ) : (
                                        <span className="text-emerald-400 text-sm font-medium">{t('table.normal')}</span>
                                    )}
                                </td>
                                <td className="py-2 px-4 min-w-[320px]">
                                    <ExplanationList explanation={row.explanation} compact />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {visible.length === 0 && (
                    <p className="text-center text-neutral-500 py-6">{t('table.noAnomalies')}</p>
                )}
            </div>
        </div>
    );
};

export default ResultsTable;
