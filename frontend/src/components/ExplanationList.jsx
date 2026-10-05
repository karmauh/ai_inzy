import { useLanguage } from '../context/LanguageContext';
import { describeExplanation } from '../utils/explanations';

// Lista cech najbardziej odbiegających od normy dla sesji oznaczonej jako anomalia
const ExplanationList = ({ explanation, compact = false }) => {
    const { t, language } = useLanguage();
    if (!explanation || explanation.length === 0) return null;

    return (
        <ul className={`flex flex-col ${compact ? 'gap-0.5' : 'gap-1'}`}>
            {explanation.map((item) => {
                const d = describeExplanation(item, t, language);
                return (
                    <li key={item.feature} className="text-xs leading-snug">
                        <span className={d.direction === 'up' ? 'text-amber-300' : 'text-sky-300'}>{d.direction === 'up' ? '▲' : '▼'}</span>{' '}
                        <span className="text-neutral-200 font-semibold">{d.label}:</span>{' '}
                        <span className="text-white font-bold">{d.value}</span>{' '}
                        <span className="text-neutral-400">({t('table.typical')} {d.typical})</span>
                    </li>
                );
            })}
        </ul>
    );
};

export default ExplanationList;
