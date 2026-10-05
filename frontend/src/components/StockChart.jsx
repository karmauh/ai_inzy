import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Scatter
} from 'recharts';
import { useLanguage } from '../context/LanguageContext';
import ExplanationList from './ExplanationList';

// Podpowiedź wykresu: data, cena i – dla anomalii – wyjaśnienie, co było nietypowe
const PriceTooltip = ({ active, payload, label, t }) => {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="bg-neutral-800 border border-neutral-600 rounded-lg p-3 shadow-xl max-w-[340px]">
      <p className="text-neutral-400 text-xs mb-1">{label}</p>
      <p className="text-white font-bold">{t('charts.closePrice')}: {typeof row.close === 'number' ? row.close.toFixed(2) : row.close}</p>
      {(row.signal === 'Buy' || row.signal === 'Sell') && (
        <p className={`text-xs font-bold mt-1 ${row.signal === 'Buy' ? 'text-primary-400' : 'text-orange-400'}`}>
          {row.signal === 'Buy' ? `▲ ${t('charts.buySignal')}` : `▼ ${t('charts.sellSignal')}`}
        </p>
      )}
      {row.is_anomaly && (
        <div className="mt-2 pt-2 border-t border-neutral-600">
          <p className="text-red-400 font-bold text-xs mb-1">⚠️ {t('charts.anomaly')}</p>
          <ExplanationList explanation={row.explanation} compact />
        </div>
      )}
    </div>
  );
};

// Strzałka sygnału: kupno pod ceną (w górę), sprzedaż nad ceną (w dół)
const SignalArrow = ({ cx, cy, direction, color }) => {
  if (cx == null || cy == null) return null;
  const up = direction === 'up';
  return (
    <svg x={cx - 10} y={up ? cy + 10 : cy - 30} width={20} height={20} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5"></line>
      <polyline points={up ? '5 12 12 5 19 12' : '5 12 12 19 19 12'}></polyline>
    </svg>
  );
};

const StockChart = ({ data }) => {
  const { t } = useLanguage();
  if (!data || data.length === 0) return <p className="text-center text-neutral-400">{t('charts.noData')}</p>;

  const formattedData = data.map(item => ({
    ...item,
    anomalyVal: item.is_anomaly ? item.close : null,
    buySignalVal: item.signal === 'Buy' ? item.close : null,
    sellSignalVal: item.signal === 'Sell' ? item.close : null
  }));

  return (
    <div className="w-full h-[400px] bg-neutral-800 p-4 rounded-lg shadow-lg">
      <h3 className="text-lg font-bold text-white mb-4">{t('charts.priceTitle')}</h3>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={formattedData}
          margin={{
            top: 5,
            right: 20,
            bottom: 5,
            left: 0,
          }}
        >
          <CartesianGrid stroke="#374151" strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="date"
            tick={{ fill: '#d1d5db' }}
            tickFormatter={(str) => {
              try {
                return str.split('T')[0];
              } catch { return str; }
            }}
            minTickGap={30}
          />
          <YAxis domain={['auto', 'auto']} tick={{ fill: '#d1d5db' }} />
          <Tooltip content={<PriceTooltip t={t} />} />
          <Legend />

          <Line
            type="monotone"
            dataKey="close"
            stroke="#14b8a6"
            dot={false}
            name={t('charts.closePrice')}
            strokeWidth={2}
          />

          <Scatter
            name={t('charts.anomaly')}
            dataKey="anomalyVal"
            fill="#ef4444"
            shape="circle"
          />

          <Scatter
            name={t('charts.buySignal')}
            dataKey="buySignalVal"
            shape={<SignalArrow direction="up" color="#14b8a6" />}
            legendType="triangle"
            fill="#14b8a6"
          />

          <Scatter
            name={t('charts.sellSignal')}
            dataKey="sellSignalVal"
            shape={<SignalArrow direction="down" color="#f97316" />}
            legendType="triangle"
            fill="#f97316"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;
