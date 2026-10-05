// Formatowanie wyjaśnień anomalii z backendu: { feature, value, typical, z }.
// Jednostka cechy decyduje o sposobie wyświetlenia wartości.
const FEATURE_UNITS = {
  return_1d: 'pctSigned',
  return_3d: 'pctSigned',
  return_7d: 'pctSigned',
  momentum_5d: 'pctSigned',
  dist_to_ema20: 'pctSigned',
  drawdown: 'pctSigned',
  volume_change: 'pctSigned',
  volatility_change: 'pctSigned',
  volatility: 'pct',
  atr: 'pct',
  body: 'pct',
  upper_shadow: 'pct',
  lower_shadow: 'pct',
  volume_ratio: 'ratio',
  rsi: 'number1',
  z_score_20: 'number2',
  bb_position: 'number2',
};

export const formatFeatureValue = (feature, value, locale = 'pl') => {
  const fmt = (v, digits) => v.toLocaleString(locale, { minimumFractionDigits: digits, maximumFractionDigits: digits });
  switch (FEATURE_UNITS[feature]) {
    case 'pctSigned':
      return `${value > 0 ? '+' : ''}${fmt(value * 100, 1)}%`;
    case 'pct':
      return `${fmt(value * 100, 2)}%`;
    case 'ratio':
      return `${fmt(value, 1)}×`;
    case 'number1':
      return fmt(value, 1);
    default:
      return fmt(value, 2);
  }
};

// Zwraca dane gotowe do wyświetlenia: etykieta cechy, wartość, wartość typowa i kierunek odchylenia
export const describeExplanation = (item, t, locale = 'pl') => ({
  label: t(`features.${item.feature}`),
  value: formatFeatureValue(item.feature, item.value, locale),
  typical: formatFeatureValue(item.feature, item.typical, locale),
  direction: item.z >= 0 ? 'up' : 'down',
  strength: Math.abs(item.z),
});
