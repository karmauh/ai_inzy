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
        <div className="mb-4">
            <h3 className="text-xs font-semibold mb-2 text-gray-400 uppercase tracking-widest">Market Search</h3>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
                <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    placeholder={t('dashboard.searchPlaceholder')}
                    className="w-full bg-slate-900/50 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all placeholder:text-gray-600"
                />
                <button
                    type="submit"
                    disabled={loading || !symbol}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white py-3 rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg active:scale-[0.98] flex items-center justify-center"
                >
                    {loading ? (
                        <span className="flex items-center gap-2">
                            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            {t('dashboard.analyzing')}
                        </span>
                    ) : t('dashboard.searchButton')}
                </button>
            </form>
        </div>
    );
};

export default TickerSearch;
