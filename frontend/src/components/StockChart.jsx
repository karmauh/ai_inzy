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
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', borderColor: '#4b5563', color: '#e8e9ea' }}
            itemStyle={{ color: '#e8e9ea' }}
            labelStyle={{ color: '#9ca3af' }}
          />
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
