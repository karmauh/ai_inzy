import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart
} from 'recharts';
import { useLanguage } from '../context/LanguageContext';

const TechnicalCharts = ({ data }) => {
  const { t } = useLanguage();
  if (!data || data.length === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
      {/* 1. Wykres RSI */}
      <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-primary-400">RSI (14)</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="date" hide />
              <YAxis domain={[0, 100]} stroke="#9ca3af" />
              <Tooltip
                 contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#e8e9ea' }}
                 labelStyle={{ color: '#9ca3af' }}
              />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
              <ReferenceLine y={30} stroke="#14b8a6" strokeDasharray="3 3" />
              <Line type="monotone" dataKey="rsi" stroke="#14b8a6" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Wykres MACD */}
      <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-primary-400">MACD (12, 26, 9)</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="date" hide />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                 contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#e8e9ea' }}
                 labelStyle={{ color: '#9ca3af' }}
              />
              <ReferenceLine y={0} stroke="#6b7280" />
              <Line type="monotone" dataKey="macd" stroke="#14b8a6" dot={false} strokeWidth={2} name="MACD" />
              <Line type="monotone" dataKey="macd_signal" stroke="#fbbf24" dot={false} strokeWidth={2} name={t('charts.signalLine')} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Wstęgi Bollingera i EMA */}
      <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-primary-400">{t('charts.bollingerTitle')}</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="date" hide />
              <YAxis domain={['auto', 'auto']} stroke="#9ca3af" />
              <Tooltip
                 contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#e8e9ea' }}
                 labelStyle={{ color: '#9ca3af' }}
                 formatter={(value) => value?.toFixed(2)}
              />
              <Area type="monotone" dataKey="bb_upper" stroke="none" fill="#14b8a6" fillOpacity={0.1} />
              <Area type="monotone" dataKey="bb_lower" stroke="none" fill="#14b8a6" fillOpacity={0.1} />
              <Line type="monotone" dataKey="close" stroke="#ffffff" dot={false} strokeWidth={1} name={t('charts.price')} />
              <Line type="monotone" dataKey="ema_20" stroke="#fbbf24" dot={false} strokeWidth={1} name="EMA 20" />
              <Line type="monotone" dataKey="ema_50" stroke="#f472b6" dot={false} strokeWidth={1} name="EMA 50" />
              <Line type="monotone" dataKey="bb_upper" stroke="#14b8a6" dot={false} strokeWidth={1} strokeDasharray="2 2" name={t('charts.bbUpper')} />
              <Line type="monotone" dataKey="bb_lower" stroke="#14b8a6" dot={false} strokeWidth={1} strokeDasharray="2 2" name={t('charts.bbLower')} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. ATR / Zmienność */}
      <div className="bg-neutral-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-primary-400">{t('charts.volatilityTitle')}</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="date" hide />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                 contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#e8e9ea' }}
                 labelStyle={{ color: '#9ca3af' }}
              />
              <Line type="monotone" dataKey="atr" stroke="#ec4899" dot={false} strokeWidth={2} name="ATR (14)" />
              <Line type="monotone" dataKey="volatility" stroke="#9ca3af" dot={false} strokeWidth={1} strokeDasharray="3 3" name="StdDev (20)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default TechnicalCharts;
