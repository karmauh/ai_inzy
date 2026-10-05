import { useEffect, useRef, useState } from 'react';
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

// Czas bez zmian suwaka (np. przy obsłudze strzałkami), po którym nowa czułość jest zatwierdzana
const SENSITIVITY_COMMIT_DELAY_MS = 700;

/**
 * Ustawienia analizy: model, okres danych, czułość (contamination) i tryb detekcji.
 * Każda zmiana jest od razu przekazywana do rodzica (który ponawia analizę), z wyjątkiem suwaka czułości –
 * ten zatwierdza wartość po puszczeniu myszy lub po chwili bez zmian (klawiatura), by nie uruchamiać
 * analizy przy każdym kroku przesuwania.
 */
const AnalysisSettings = ({ model, period, contamination, mode, disabled, onModelChange, onPeriodChange, onContaminationChange, onModeChange }) => {
    const { t } = useLanguage();
    const [draftContamination, setDraftContamination] = useState(contamination);
    const dragging = useRef(false);

    useEffect(() => setDraftContamination(contamination), [contamination]);

    const commitContamination = () => {
        dragging.current = false;
        if (draftContamination !== contamination) onContaminationChange(draftContamination);
    };

    // Zatwierdzenie po chwili bez zmian (klawiatura); podczas przeciągania myszą czekamy na jej puszczenie
    useEffect(() => {
        if (draftContamination === contamination || dragging.current) return undefined;
        const timer = setTimeout(() => onContaminationChange(draftContamination), SENSITIVITY_COMMIT_DELAY_MS);
        return () => clearTimeout(timer);
    }, [draftContamination, contamination, onContaminationChange]);

    const percent = Math.round(draftContamination * 100);

    return (
        <div className="mb-8 bg-neutral-800 p-6 rounded-xl shadow-2xl border border-neutral-700 animate-fade-in-up">
            <h2 className="text-lg font-bold text-white mb-5">{t('settings.title')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                <Field title={t('settings.model')} hint={t(`benchmark.models.${model}_meta`)}>
                    <select
                        value={model}
                        onChange={(e) => onModelChange(e.target.value)}
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
                    <SegmentedControl options={PERIODS} value={period} onChange={onPeriodChange} disabled={disabled}
                                      label={(p) => t(`settings.periods.${p}`)} />
                </Field>

                <Field title={`${t('settings.sensitivity')}: ${percent}%`} hint={t('settings.sensitivityHint')}>
                    <input
                        type="range"
                        min={1}
                        max={15}
                        step={1}
                        value={percent}
                        disabled={disabled}
                        onChange={(e) => setDraftContamination(Number(e.target.value) / 100)}
                        onPointerDown={() => { dragging.current = true; }}
                        onPointerUp={commitContamination}
                        onBlur={commitContamination}
                        aria-label={t('settings.sensitivity')}
                        className="w-full accent-primary-500 disabled:cursor-wait"
                    />
                    <div className="flex justify-between text-[10px] text-neutral-500">
                        <span>1%</span><span>15%</span>
                    </div>
                </Field>

                <Field title={t('mode.title')} hint={t(`mode.${mode}Desc`)}>
                    <SegmentedControl options={MODES} value={mode} onChange={onModeChange} disabled={disabled}
                                      label={(m) => t(`mode.${m}`)} />
                </Field>
            </div>
        </div>
    );
};

export default AnalysisSettings;
