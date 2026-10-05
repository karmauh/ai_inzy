import { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';

const GearIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5" aria-hidden="true">
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
);

const TickerSearch = ({ onSearch, loading, settings, settingsOpen, settingsPending, onToggleSettings }) => {
    const { t } = useLanguage();
    const [symbol, setSymbol] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (symbol.trim()) {
            onSearch(symbol.trim().toUpperCase());
        }
    };

    // Krótkie podsumowanie ustawień, z którymi zostanie wykonana analiza (widoczne także przy zwiniętym panelu)
    const summary = [
        t(`benchmark.models.${settings.model}_name`),
        t(`settings.periods.${settings.period}`),
        `${t('settings.sensitivity').toLowerCase()} ${Math.round(settings.contamination * 100)}%`,
        t(`mode.${settings.mode}`).toLowerCase(),
    ].join(' · ');

    return (
        <div className="mb-4">
            <h3 className="text-xs font-semibold mb-2 text-neutral-400 uppercase tracking-widest">{t('dashboard.marketSearch')}</h3>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
                <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    placeholder={t('dashboard.searchPlaceholder')}
                    className="w-full bg-neutral-700 border border-neutral-600 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-400 transition-all placeholder:text-neutral-500"
                />
                <div className="flex gap-2">
                    <button
                        type="submit"
                        disabled={loading || !symbol}
                        className="flex-1 bg-primary-600 hover:bg-primary-500 text-white py-3 rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg active:scale-[0.98] flex items-center justify-center"
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
                    <button
                        type="button"
                        onClick={onToggleSettings}
                        aria-label={t('settings.title')}
                        aria-expanded={settingsOpen}
                        aria-controls="analysis-settings"
                        title={t('settings.title')}
                        className={`relative px-4 rounded-xl border transition-all ${settingsOpen ? 'bg-primary-600/20 border-primary-500 text-primary-400' : 'bg-neutral-700 border-neutral-600 text-neutral-300 hover:text-white hover:border-neutral-500'}`}
                    >
                        <GearIcon />
                        {settingsPending && <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-amber-400 border-2 border-neutral-800" title={t('settings.pending')} />}
                    </button>
                </div>
                <button type="button" onClick={onToggleSettings} className="text-left text-xs text-neutral-500 hover:text-neutral-300 transition-colors">
                    {summary}
                    {settingsPending && <span className="text-amber-300"> · {t('settings.pendingShort')}</span>}
                </button>
            </form>
        </div>
    );
};

export default TickerSearch;
