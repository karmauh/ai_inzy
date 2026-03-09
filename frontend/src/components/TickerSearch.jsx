import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

const TickerSearch = ({ onSearch, loading }) => {
    const { t } = useLanguage();
    const [symbol, setSymbol] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (symbol.trim()) {
            onSearch(symbol.trim().toUpperCase());
        }
    };

    return (
        <div className="bg-slate-800 p-6 rounded-lg shadow-lg mb-8">
            <h2 className="text-xl font-bold mb-4 text-blue-400">Market Search</h2>
            <form onSubmit={handleSubmit} className="flex gap-4">
                <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    placeholder={t('dashboard.searchPlaceholder')}
                    className="flex-1 bg-slate-700 text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    type="submit"
                    disabled={loading || !symbol}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {loading ? t('dashboard.analyzing') : t('dashboard.searchButton')}
                </button>
            </form>
        </div>
    );
};

export default TickerSearch;
