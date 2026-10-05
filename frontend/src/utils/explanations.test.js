import { describe, expect, it } from 'vitest';
import { describeExplanation, formatFeatureValue } from './explanations';
import { translate, translations } from './translations';

describe('formatFeatureValue', () => {
  it('formatuje stopy zwrotu ze znakiem w procentach', () => {
    expect(formatFeatureValue('return_1d', -0.0999, 'en')).toBe('-10.0%');
    expect(formatFeatureValue('return_1d', 0.155, 'en')).toBe('+15.5%');
  });

  it('formatuje wolumen względem średniej jako krotność', () => {
    expect(formatFeatureValue('volume_ratio', 4.0213, 'en')).toBe('4.0×');
  });

  it('formatuje RSI jako liczbę', () => {
    expect(formatFeatureValue('rsi', 70.84, 'en')).toBe('70.8');
  });

  it('używa przecinka dziesiętnego w języku polskim', () => {
    expect(formatFeatureValue('return_1d', -0.0999, 'pl')).toBe('-10,0%');
  });
});

describe('describeExplanation', () => {
  it('zwraca etykietę, wartości i kierunek odchylenia', () => {
    const t = (key) => translate('pl', key);
    const result = describeExplanation({ feature: 'volume_ratio', value: 4.02, typical: 1.05, z: 8.7 }, t, 'pl');

    expect(result).toEqual({ label: translate('pl', 'features.volume_ratio'), value: '4,0×', typical: '1,1×', direction: 'up', strength: 8.7 });
  });

  it('ma tłumaczenie dla każdej cechy modelu w obu językach', () => {
    const features = ['return_1d', 'return_3d', 'return_7d', 'momentum_5d', 'dist_to_ema20', 'drawdown', 'volume_change',
      'volatility_change', 'volatility', 'atr', 'body', 'upper_shadow', 'lower_shadow', 'volume_ratio', 'rsi', 'z_score_20', 'bb_position'];
    for (const language of Object.keys(translations)) {
      for (const f of features) expect(translate(language, `features.${f}`), `${language}:${f}`).not.toBe(`features.${f}`);
    }
  });
});
