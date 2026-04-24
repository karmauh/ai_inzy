import React, { useState } from 'react';
import { BarChart, Bar, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { exportCSV } from '../services/api';
import { useLanguage } from '../context/LanguageContext';

const formatPercent = (val) => `${(val * 100).toFixed(1)}%`;

const CustomTooltip = ({ active, payload, label, t }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-slate-900/90 p-4 border border-slate-600 rounded-xl shadow-2xl backdrop-blur-md max-w-[300px]">
                <p className="font-black text-gray-100 mb-3 border-b border-slate-700 pb-2">{label}</p>
                <div className="space-y-3">
                    {payload.map((entry, index) => {
                        let descKey = 'benchmark.metrics.defaultDesc';
                        if (entry.name === 'Precision') descKey = 'benchmark.metrics.precisionDesc';
                        if (entry.name === 'Recall') descKey = 'benchmark.metrics.recallDesc';
                        if (entry.name === 'F1 Score') descKey = 'benchmark.metrics.f1Desc';
                        
                        return (
                            <div key={index} className="flex flex-col">
                                <div className="flex justify-between items-center">
                                    <span style={{ color: entry.color }} className="font-bold tracking-wide">{entry.name}</span>
                                    <span className="text-gray-100 font-black tracking-wider bg-slate-800 px-2 py-0.5 rounded shadow-inner">{formatPercent(entry.value)}</span>
                                </div>
                                <span className="text-[10px] text-gray-400 mt-1 leading-tight">{t(descKey)}</span>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }
    return null;
};

const ModelBenchmark = ({ evaluationData, loading, onRunBenchmark, onSelectModel }) => {
    const { t } = useLanguage();
    const [primaryMetric, setPrimaryMetric] = useState('f1_score');
    const [sortConfig, setSortConfig] = useState({ key: 'f1_score', direction: 'desc' });
    const [chartType, setChartType] = useState('bar'); // 'bar' | 'radar'

    if (loading) {
        return (
            <div className="space-y-8 animate-fade-in-up">
                <div className="bg-slate-800 p-6 rounded-xl shadow-2xl flex flex-col items-center justify-center min-h-[400px] border border-slate-700/50">
                    <div className="animate-spin text-5xl mb-6">🔄</div>
                    <p className="text-gray-200 font-bold text-lg">{t('benchmark.loading.title')}</p>
                    <p className="text-sm text-gray-400 mt-2">{t('benchmark.loading.subtitle')}</p>
                </div>
            </div>
        );
    }

    if (!evaluationData) {
        return (
            <div className="space-y-8 animate-fade-in-up">
                <div className="bg-slate-800 p-6 rounded-xl shadow-lg flex flex-col items-center justify-center min-h-[400px] border border-slate-700/50 text-center">
                    <div className="text-5xl opacity-40 mb-6 drop-shadow-md">📊</div>
                    <h2 className="text-gray-200 font-bold text-2xl mb-3">{t('benchmark.empty.title')}</h2>
                    <p className="text-gray-400 mb-8 max-w-lg">
                        {t('benchmark.empty.desc')}
                    </p>
                    <button
                        onClick={onRunBenchmark}
                        className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-8 py-3 rounded-xl shadow-lg transition-all font-bold tracking-wide transform hover:scale-105"
                    >
                        {t('benchmark.empty.button')}
                    </button>
                </div>
            </div>
        );
    }

    let modelsList = Object.entries(evaluationData).filter(([_, data]) => !data.error).map(([key, data]) => ({
        key,
        name: t(`benchmark.models.${key}_name`) !== `benchmark.models.${key}_name` ? t(`benchmark.models.${key}_name`) : key,
        meta: t(`benchmark.models.${key}_meta`) !== `benchmark.models.${key}_meta` ? t(`benchmark.models.${key}_meta`) : '',
        precision: data.metrics?.precision || 0,
        recall: data.metrics?.recall || 0,
        f1_score: data.metrics?.f1_score || 0,
        cm: data.confusion_matrix || {},
        isError: false
    }));

    const errorModelsList = Object.entries(evaluationData).filter(([_, data]) => data.error).map(([key, data]) => ({
        key,
        name: t(`benchmark.models.${key}_name`) !== `benchmark.models.${key}_name` ? t(`benchmark.models.${key}_name`) : key,
        error: data.error,
        isError: true
    }));

    const handleExportCSV = () => {
        const payload = modelsList.map(m => ({
            [t('benchmark.table.model')]: m.name,
            [t('benchmark.table.precision')]: formatPercent(m.precision),
            [t('benchmark.table.recall')]: formatPercent(m.recall),
            [t('benchmark.table.f1Score')]: formatPercent(m.f1_score),
            [`${t('benchmark.table.tooltipTp')}`]: m.cm.true_positives || 0,
            [`${t('benchmark.table.tooltipFp')}`]: m.cm.false_positives || 0,
            [`${t('benchmark.table.tooltipTn')}`]: m.cm.true_negatives || 0,
            [`${t('benchmark.table.tooltipFn')}`]: m.cm.false_negatives || 0
        }));
        exportCSV(payload);
    };

    const handleSort = (key) => {
        let direction = 'desc';
        if (sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc';
        }
        setSortConfig({ key, direction });
    };

    modelsList.sort((a, b) => {
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];
        
        if (['tp', 'tn', 'fp', 'fn'].includes(sortConfig.key)) {
            const map = { tp: 'true_positives', tn: 'true_negatives', fp: 'false_positives', fn: 'false_negatives'};
            aVal = a.cm[map[sortConfig.key]] || 0;
            bVal = b.cm[map[sortConfig.key]] || 0;
        }

        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });

    const getBestModel = (metricName) => {
        if (modelsList.length === 0) return null;
        return [...modelsList].sort((a, b) => b[metricName] - a[metricName])[0];
    };

    const bestByPrecision = getBestModel('precision');
    const bestByRecall = getBestModel('recall');
    const bestByPrimary = getBestModel(primaryMetric);

    const chartData = modelsList.map(m => ({
        name: m.name,
        precision: m.precision,
        recall: m.recall,
        f1_score: m.f1_score,
    }));

    const renderInsights = () => {
        if (!bestByPrimary || !bestByPrecision || !bestByRecall) return null;

        const metricMap = {
            'f1_score': t('benchmark.header.metricF1'),
            'precision': t('benchmark.header.metricPrecision'),
            'recall': t('benchmark.header.metricRecall')
        };

        return (
            <div className="bg-slate-900/50 p-5 rounded-xl border border-blue-500/30 mb-8 mx-auto xl:w-[90%] shadow-inner transition-all flex flex-col gap-4 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-blue-500 rounded-l-xl opacity-50"></div>
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">💡</span>
                    <h3 className="text-gray-100 font-bold text-lg">{t('benchmark.insights.title')}</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                        <p className="text-slate-300 text-sm leading-relaxed">
                            {t('benchmark.insights.mainStart')} <strong className="text-white">({metricMap[primaryMetric]})</strong>{t('benchmark.insights.mainMiddle')} <strong className="text-blue-400">{bestByPrimary.name}</strong> {t('benchmark.insights.mainValue')} <span className="text-blue-300 font-bold">{formatPercent(bestByPrimary[primaryMetric])}</span> {t('benchmark.insights.mainEnd')}
                        </p>
                        <ul className="text-xs text-slate-400 space-y-2 mt-2 list-disc pl-4">
                            <li>{t('benchmark.insights.precisionWinner')} <span className="text-gray-200">{bestByPrecision.name}</span></li>
                            <li>{t('benchmark.insights.recallWinner')} <span className="text-gray-200">{bestByRecall.name}</span></li>
                        </ul>
                    </div>
                    <div className="bg-slate-800/80 p-4 rounded border border-slate-700 h-full flex flex-col justify-center">
                        <h4 className="text-xs uppercase tracking-widest text-gray-500 font-bold mb-2">{t('benchmark.insights.tradeoffTitle')}</h4>
                        <p className="text-xs text-gray-400 leading-relaxed italic">
                            {t('benchmark.insights.tradeoffDesc')}
                        </p>
                    </div>
                </div>
            </div>
        );
    };

    const SortIndicator = ({ columnKey }) => {
        if (sortConfig.key !== columnKey) return null;
        return <span className="ml-1 text-purple-400">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>;
    };

    return (
        <div className="space-y-8 animate-fade-in-up">
            <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700/50">
                <header className="mb-6 flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4">
                    <div>
                        <h2 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">{t('benchmark.header.title')}</h2>
                        <p className="text-sm font-semibold mt-1 text-gray-400">{t('benchmark.header.subtitle')}</p>
                    </div>
                    <div className="flex flex-col sm:flex-row items-center gap-3">
                        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
                            <button onClick={() => setChartType('bar')} className={`px-3 py-1.5 text-xs font-bold rounded transition-all ${chartType === 'bar' ? 'bg-slate-700 text-white shadow' : 'text-gray-400 hover:text-white'}`}>{t('benchmark.header.barChart')}</button>
                            <button onClick={() => setChartType('radar')} className={`px-3 py-1.5 text-xs font-bold rounded transition-all ${chartType === 'radar' ? 'bg-slate-700 text-white shadow' : 'text-gray-400 hover:text-white'}`}>{t('benchmark.header.radarChart')}</button>
                        </div>
                        <div className="h-6 w-px bg-slate-700 hidden sm:block"></div>
                        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
                            <button onClick={() => setPrimaryMetric('f1_score')} className={`px-4 py-1.5 text-xs font-bold rounded transition-all ${primaryMetric === 'f1_score' ? 'bg-purple-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}>{t('benchmark.header.metricF1')}</button>
                            <button onClick={() => setPrimaryMetric('precision')} className={`px-4 py-1.5 text-xs font-bold rounded transition-all ${primaryMetric === 'precision' ? 'bg-blue-500 text-white shadow' : 'text-gray-400 hover:text-white'}`}>{t('benchmark.header.metricPrecision')}</button>
                            <button onClick={() => setPrimaryMetric('recall')} className={`px-4 py-1.5 text-xs font-bold rounded transition-all ${primaryMetric === 'recall' ? 'bg-emerald-500 text-white shadow' : 'text-gray-400 hover:text-white'}`}>{t('benchmark.header.metricRecall')}</button>
                        </div>
                        <button onClick={handleExportCSV} className="bg-green-600/20 hover:bg-green-600/40 text-green-400 border border-green-500/30 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors shadow">
                            {t('benchmark.header.csv')}
                        </button>
                    </div>
                </header>

                {renderInsights()}
                
                <div className="h-[430px] mb-10 bg-slate-900/30 p-6 rounded-xl border border-slate-700/50">
                    <ResponsiveContainer width="100%" height="100%">
                        {chartType === 'bar' ? (
                            <BarChart data={chartData.reverse()} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#cbd5e1', fontWeight: 600 }} tickLine={false} axisLine={{ stroke: '#475569' }}/>
                                <YAxis stroke="#94a3b8" tickFormatter={formatPercent} tickLine={false} axisLine={{ stroke: '#475569' }} domain={[0, 1]} />
                                <Tooltip content={<CustomTooltip t={t} />} cursor={{ fill: '#334155', opacity: 0.4 }} />
                                <Legend wrapperStyle={{ color: '#94a3b8', paddingTop: '20px' }} iconType="circle" />
                                <Bar dataKey="precision" name="Precision" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={30} />
                                <Bar dataKey="recall" name="Recall" fill="#10b981" radius={[6, 6, 0, 0]} barSize={30} />
                                <Bar dataKey="f1_score" name="F1 Score" fill="#8b5cf6" radius={[6, 6, 0, 0]} barSize={30} />
                            </BarChart>
                        ) : (
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
                                <PolarGrid stroke="#334155" />
                                <PolarAngleAxis dataKey="name" tick={{ fill: '#cbd5e1', fontWeight: 600 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 1]} tickFormatter={formatPercent} tick={{ fill: '#94a3b8' }} />
                                <Radar name="Precision" dataKey="precision" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                                <Radar name="Recall" dataKey="recall" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                                <Radar name="F1 Score" dataKey="f1_score" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                                <Legend wrapperStyle={{ color: '#94a3b8', paddingTop: '20px' }} iconType="circle" />
                                <Tooltip content={<CustomTooltip t={t} />} />
                            </RadarChart>
                        )}
                    </ResponsiveContainer>
                </div>

                <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-slate-600 rounded-lg">
                    <table className="w-full text-left text-gray-300 min-w-max">
                        <thead className="bg-slate-900 sticky top-0">
                            <tr className="border-b border-gray-700 select-none">
                                <th onClick={() => handleSort('name')} className="py-4 px-5 font-bold tracking-wider text-gray-400 hover:text-gray-200 cursor-pointer uppercase text-xs transition-colors">
                                    {t('benchmark.table.model')} <SortIndicator columnKey="name" />
                                </th>
                                <th onClick={() => handleSort('precision')} className={`py-4 px-5 font-bold tracking-wider hover:text-blue-300 cursor-pointer text-xs transition-colors ${primaryMetric === 'precision' ? 'text-blue-400' : 'text-gray-400'}`}>
                                    {t('benchmark.table.precision')} <SortIndicator columnKey="precision" />
                                </th>
                                <th onClick={() => handleSort('recall')} className={`py-4 px-5 font-bold tracking-wider hover:text-emerald-300 cursor-pointer text-xs transition-colors ${primaryMetric === 'recall' ? 'text-emerald-400' : 'text-gray-400'}`}>
                                    {t('benchmark.table.recall')} <SortIndicator columnKey="recall" />
                                </th>
                                <th onClick={() => handleSort('f1_score')} className={`py-4 px-5 font-bold tracking-wider hover:text-purple-300 cursor-pointer text-xs transition-colors ${primaryMetric === 'f1_score' ? 'text-purple-400' : 'text-gray-400'}`}>
                                    {t('benchmark.table.f1Score')} <SortIndicator columnKey="f1_score" />
                                </th>
                                <th className="py-4 px-5 font-bold tracking-wider text-gray-400 text-xs text-center border-l border-slate-700/50">
                                    {t('benchmark.table.confusionMatrix')}
                                </th>
                                <th className="py-4 px-5 font-bold tracking-wider text-gray-400 text-xs text-right border-l border-slate-700/50">
                                    {t('benchmark.table.actions')}
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {modelsList.map((m) => {
                                const isWinner = bestByPrimary?.key === m.key;
                                return (
                                    <tr key={m.key} className={`border-b border-slate-700 transition-colors group ${isWinner ? 'bg-blue-900/10 hover:bg-blue-900/20' : 'hover:bg-slate-800/80'}`}>
                                        <td className="py-4 px-5 align-middle">
                                            <div className="flex flex-col relative w-full">
                                                <div className="flex items-center gap-2">
                                                    <span className={`font-black tracking-wide text-[14px] ${isWinner ? 'text-blue-300' : 'text-gray-100'}`}>{m.name}</span>
                                                    {isWinner && <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-[10px] uppercase tracking-wider rounded border border-blue-500/30 font-bold ml-1">{t('benchmark.table.leader')}</span>}
                                                </div>
                                                <span className="text-xs text-gray-500 font-medium leading-relaxed mt-1.5 max-w-[240px] group-hover:text-gray-400 transition-colors">{m.meta}</span>
                                            </div>
                                        </td>
                                        <td className={`py-4 px-5 align-middle font-bold text-[14px] ${primaryMetric === 'precision' ? 'text-blue-300 bg-slate-900/30' : ''}`}>{formatPercent(m.precision)}</td>
                                        <td className={`py-4 px-5 align-middle font-bold text-[14px] ${primaryMetric === 'recall' ? 'text-emerald-400 bg-slate-900/30' : ''}`}>{formatPercent(m.recall)}</td>
                                        <td className={`py-4 px-5 align-middle font-black text-[15px] ${primaryMetric === 'f1_score' ? 'text-purple-400 bg-slate-900/30' : 'text-gray-300'}`}>{formatPercent(m.f1_score)}</td>
                                        <td className="py-4 px-5 align-middle bg-slate-900/10 border-l border-slate-700/50">
                                            <div className="flex justify-center gap-2 text-[12px] font-mono whitespace-nowrap opacity-90">
                                                <div className="flex flex-col gap-1">
                                                    <div onClick={() => handleSort('tp')} className="bg-green-900/40 border border-green-500/30 text-green-300 px-3 py-1 rounded cursor-pointer hover:bg-green-900/60 transition-colors flex justify-between gap-3 items-center min-w-[120px]" title={t('benchmark.table.tooltipTp')}>
                                                        <span>{t('benchmark.table.tp')} <SortIndicator columnKey="tp" /></span>
                                                        <span className="font-bold text-[14px]">{m.cm.true_positives || 0}</span>
                                                    </div>
                                                    <div onClick={() => handleSort('fp')} className="bg-red-900/40 border border-red-500/30 text-red-300 px-3 py-1 rounded cursor-pointer hover:bg-red-900/60 transition-colors flex justify-between gap-3 items-center min-w-[120px]" title={t('benchmark.table.tooltipFp')}>
                                                        <span>{t('benchmark.table.fp')} <SortIndicator columnKey="fp" /></span>
                                                        <span className="font-bold text-[14px]">{m.cm.false_positives || 0}</span>
                                                    </div>
                                                </div>
                                                <div className="flex flex-col gap-1">
                                                    <div onClick={() => handleSort('tn')} className="bg-slate-700/50 border border-slate-600/50 text-gray-300 px-3 py-1 rounded cursor-pointer hover:bg-slate-700/80 transition-colors flex justify-between gap-3 items-center min-w-[120px]" title={t('benchmark.table.tooltipTn')}>
                                                        <span>{t('benchmark.table.tn')} <SortIndicator columnKey="tn" /></span>
                                                        <span className="font-bold text-[14px]">{m.cm.true_negatives || 0}</span>
                                                    </div>
                                                    <div onClick={() => handleSort('fn')} className="bg-yellow-900/40 border border-yellow-500/30 text-yellow-300 px-3 py-1 rounded cursor-pointer hover:bg-yellow-900/60 transition-colors flex justify-between gap-3 items-center min-w-[120px]" title={t('benchmark.table.tooltipFn')}>
                                                        <span>{t('benchmark.table.fn')} <SortIndicator columnKey="fn" /></span>
                                                        <span className="font-bold text-[14px]">{m.cm.false_negatives || 0}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-5 align-middle text-right border-l border-slate-700/50">
                                            <button 
                                                onClick={() => onSelectModel && onSelectModel(m.key)}
                                                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded shadow transition-colors font-bold text-xs"
                                                title={`${t('benchmark.table.selectModelTitle')} ${m.name}`}
                                            >
                                                {t('benchmark.table.selectModel')}
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                            {errorModelsList.map((errObj) => (
                                <tr key={errObj.key} className="border-b border-gray-700 hover:bg-slate-700/30 transition-colors">
                                    <td className="py-4 px-5 font-medium text-gray-500 relative group cursor-help">
                                        {errObj.name}
                                    </td>
                                    <td colSpan="5" className="py-4 px-5 text-red-500 font-bold bg-red-900/10">{t('benchmark.table.calcError')} {errObj.error}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ModelBenchmark;
