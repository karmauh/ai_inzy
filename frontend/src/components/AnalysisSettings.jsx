import { useLanguage } from '../context/LanguageContext';

const MODELS = ['isolation_forest', 'lof', 'ocsvm', 'autoencoder', 'ensemble'];
const PERIODS = ['6mo', '1y', '2y', '5y'];
const MODES = ['batch', 'walk_forward'];

const SegmentedControl = ({ options, value, onChange, disabled, label }) => (
    <div className="flex flex-wrap bg-neutral-900 rounded-lg p-1 border border-neutral-700 w-fit">
        {options.map((option) => (
            <button
                key={option}
                onClick={() => onChange(option)}
                disabled={disabled}
                className={`px-3 py-1.5 text-xs font-bold rounded transition-all disabled:cursor-wait ${value === option ? 'bg-primary-600 text-white shadow' : 'text-neutral-400 hover:text-white'}`}
            >
                {label(option)}
            </button>
        ))}
    </div>
);

const Field = ({ title, children, hint }) => (
    <div className="flex flex-col gap-2 min-w-0">
        <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">{title}</span>
        {children}
        {hint && <p className="text-xs text-neutral-500 leading-relaxed">{hint}</p>}
    </div>
);

/**
 * Ustawienia analizy (zaawansowane): model, okres danych, czułość i tryb detekcji.
 * Komponent edytuje wyłącznie szkic (value/onChange) – nic nie jest przeliczane, dopóki użytkownik
 * nie kliknie "Zastosuj ustawienia" albo nie uruchomi wyszukiwania.
 */
const AnalysisSettings = ({ value, onChange, dirty, hasResults, disabled, onApply, onReset, onClose }) => {
    const { t } = useLanguage();
    const percent = Math.round(value.contamination * 100);

    return (
        <div id="analysis-settings" className="mb-8 bg-neutral-800 p-6 rounded-xl shadow-2xl border border-neutral-700 animate-fade-in-up">
            <div className="flex items-start justify-between gap-4 mb-5">
                <div>
                    <h2 className="text-lg font-bold text-white">{t('settings.title')}</h2>
                    <p className="text-xs text-neutral-500 mt-1">{t(hasResults ? 'settings.applyHint' : 'settings.searchHint')}</p>
                </div>
                <button onClick={onClose} aria-label={t('settings.close')} title={t('settings.close')}
                        className="text-neutral-400 hover:text-white text-xl leading-none px-2">×</button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                <Field title={t('settings.model')} hint={t(`benchmark.models.${value.model}_meta`)}>
                    <select
                        value={value.model}
                        onChange={(e) => onChange({ model: e.target.value })}
                        disabled={disabled}
                        aria-label={t('settings.model')}
                        className="bg-neutral-900 border border-neutral-700 text-neutral-100 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-primary-400 disabled:cursor-wait"
                    >
                        {MODELS.map((m) => (
                            <option key={m} value={m}>{t(`benchmark.models.${m}_name`)}</option>
                        ))}
                    </select>
                </Field>

                <Field title={t('settings.period')} hint={t('settings.periodHint')}>
                    <SegmentedControl options={PERIODS} value={value.period} onChange={(period) => onChange({ period })}
                                      disabled={disabled} label={(p) => t(`settings.periods.${p}`)} />
                </Field>

                <Field title={`${t('settings.sensitivity')}: ${percent}%`} hint={t('settings.sensitivityHint')}>
                    <input
                        type="range"
                        min={1}
                        max={15}
                        step={1}
                        value={percent}
                        disabled={disabled}
                        onChange={(e) => onChange({ contamination: Number(e.target.value) / 100 })}
                        aria-label={t('settings.sensitivity')}
                        className="w-full accent-primary-500 disabled:cursor-wait"
                    />
                    <div className="flex justify-between text-[10px] text-neutral-500">
                        <span>1%</span><span>15%</span>
                    </div>
                </Field>

                <Field title={t('mode.title')} hint={t(`mode.${value.mode}Desc`)}>
                    <SegmentedControl options={MODES} value={value.mode} onChange={(mode) => onChange({ mode })}
                                      disabled={disabled} label={(m) => t(`mode.${m}`)} />
                </Field>
            </div>

            {hasResults && (
                <div className="mt-6 pt-4 border-t border-neutral-700 flex flex-col sm:flex-row sm:items-center justify-end gap-3">
                    {dirty && <span className="text-xs text-amber-300 sm:mr-auto">● {t('settings.pending')}</span>}
                    <button
                        onClick={onReset}
                        disabled={!dirty || disabled}
                        className="px-4 py-2 rounded-lg text-sm font-bold text-neutral-300 border border-neutral-600 hover:bg-neutral-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                        {t('settings.reset')}
                    </button>
                    <button
                        onClick={onApply}
                        disabled={!dirty || disabled}
                        className="px-5 py-2 rounded-lg text-sm font-bold text-white bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow"
                    >
                        {t('settings.apply')}
                    </button>
                </div>
            )}
        </div>
    );
};

export default AnalysisSettings;
