import React from 'react';
import { useLanguage } from '../context/LanguageContext';

const AssessmentPanel = ({ assessment }) => {
    const { t } = useLanguage();
    if (!assessment) return null;

    const { sentiment, recommendation, summary, confidence } = assessment;

    let sentimentColor = 'text-gray-400';
    if (sentiment.includes('Bullish')) sentimentColor = 'text-green-400';
    if (sentiment.includes('Bearish')) sentimentColor = 'text-red-400';

    // Kolory dla rekomendacji
    let recColor = 'bg-gray-600';
    if (recommendation === 'Buy' || recommendation === 'Kupuj') recColor = 'bg-green-600';
    if (recommendation === 'Sell' || recommendation === 'Sprzedaj') recColor = 'bg-red-600';

    return (
        <div className="bg-slate-800 p-6 rounded-lg shadow-lg border-l-4 border-purple-500">
            <h2 className="text-2xl font-bold mb-4 text-purple-400 flex items-center gap-2">
                <span>🤖</span> {t('assessment.title')}
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-slate-700/50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">{t('assessment.sentiment')}</p>
                    <p className={`text-xl font-bold ${sentimentColor}`}>{sentiment}</p>
                </div>
                
                <div className="bg-slate-700/50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">{t('assessment.recommendation')}</p>
                    <span className={`inline-block px-4 py-1 rounded-full text-white font-bold text-lg ${recColor}`}>
                        {recommendation}
                    </span>
                </div>

                <div className="bg-slate-700/50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">{t('assessment.confidence')}</p>
                    <p className="text-xl font-bold text-blue-300">{confidence}</p>
                </div>
            </div>

            <div className="bg-slate-700/30 p-4 rounded-lg">
                <h4 className="text-gray-500 text-xs uppercase mb-2">{t('assessment.summary')}</h4>
                <p className="text-gray-300 italic leading-relaxed">"{summary}"</p>
            </div>
        </div>
    );
};

export default AssessmentPanel;
