import { describe, expect, it } from 'vitest';
import { translate, translations } from './translations';

const collectKeys = (obj, prefix = '') =>
  Object.entries(obj).flatMap(([key, value]) =>
    typeof value === 'object' && value !== null
      ? collectKeys(value, `${prefix}${key}.`)
      : [`${prefix}${key}`]
  );

describe('translations', () => {
  it('pl i en mają identyczny zestaw kluczy', () => {
    expect(collectKeys(translations.en).sort()).toEqual(collectKeys(translations.pl).sort());
  });

  it('żadne tłumaczenie nie jest puste', () => {
    for (const language of Object.keys(translations)) {
      for (const key of collectKeys(translations[language])) {
        expect(translate(language, key), `${language}:${key}`).not.toBe('');
      }
    }
  });

  it('obsługuje wartości kanoniczne zwracane przez backend', () => {
    for (const value of ['Bullish', 'Bearish', 'Neutral', 'Buy', 'Sell', 'Hold', 'High', 'Medium', 'Low']) {
      expect(translate('pl', `assessment.values.${value}`)).not.toBe(`assessment.values.${value}`);
    }
    expect(translate('pl', 'assessment.values.Buy')).toBe('Kupuj');
  });
});

describe('translate', () => {
  it('zwraca klucz dla brakującego tłumaczenia lub węzła niebędącego tekstem', () => {
    expect(translate('pl', 'nie.istnieje')).toBe('nie.istnieje');
    expect(translate('pl', 'dashboard')).toBe('dashboard');
    expect(translate('xx', 'dashboard.error')).toBe('dashboard.error');
  });
});
