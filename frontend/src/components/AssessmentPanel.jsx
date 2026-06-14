import React from 'react';
import { useLanguage } from '../context/LanguageContext';

const AssessmentPanel = ({ assessment }) => {
    const { t } = useLanguage();
    if (!assessment) return null;

    const { sentiment, recommendation, summary, confidence } = assessment;

    let sentimentColor = 'text-neutral-400';
    if (sentiment.includes('Bullish')) sentimentColor = 'text-emerald-400';
    if (sentiment.includes('Bearish')) sentimentColor = 'text-red-400';

    // Kolory dla rekomendacji
    let recColor = 'bg-neutral-600';
    if (recommendation === 'Buy' || recommendation === 'Kupuj') recColor = 'bg-emerald-600';
    if (recommendation === 'Sell' || recommendation === 'Sprzedaj') recColor = 'bg-red-600';

    const renderSummary = (text) => {
        if (!text) return null;

        const paragraphs = text.split(/\n+/).filter(p => p.trim() !== '');

        return paragraphs.map((paragraph, index) => {
            const parts = paragraph.split(/(\*\*.*?\*\*)/g);
            return (
                <p key={index} className="mb-3 last:mb-0 text-neutral-300 leading-relaxed font-light">
                    {parts.map((part, i) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={i} className="text-primary-400 font-semibold">{part.slice(2, -2)}</strong>;
                        }
                        return <span key={i}>{part}</span>;
                    })}
                </p>
            );
        });
    };

    return (
        <div className="bg-neutral-800 rounded-xl shadow-2xl overflow-hidden border border-neutral-700 transition-all hover:border-primary-500/50">
            <div className="bg-neutral-700 p-4 border-b border-neutral-600 flex justify-between items-center">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="text-primary-400">📊</span> {t('assessment.title')}
                </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6 p-6">
                <div className="bg-neutral-700 p-4 rounded-lg text-center">
                    <p className="text-sm text-neutral-400 uppercase tracking-wider mb-1">{t('assessment.sentiment')}</p>
                    <p className={`text-xl font-bold ${sentimentColor}`}>{sentiment}</p>
                </div>

                <div className="bg-neutral-700 p-4 rounded-lg text-center">
                    <p className="text-sm text-neutral-400 uppercase tracking-wider mb-1">{t('assessment.recommendation')}</p>
                    <span className={`inline-block px-4 py-1 rounded-full text-white font-bold text-lg ${recColor}`}>
                        {recommendation}
                    </span>
                </div>

                <div className="bg-neutral-700 p-4 rounded-lg text-center">
                    <p className="text-sm text-neutral-400 uppercase tracking-wider mb-1">{t('assessment.confidence')}</p>
                    <p className="text-xl font-bold text-primary-400">{confidence}</p>
                </div>
            </div>

            <div className="bg-neutral-700/50 p-6 rounded-lg">
                <h4 className="text-neutral-400 text-xs uppercase mb-3 font-semibold">{t('assessment.summary')}</h4>
                <div className="text-neutral-300 text-sm">
                    {renderSummary(summary)}
                </div>
            </div>
        </div>
    );
};

export default AssessmentPanel;
