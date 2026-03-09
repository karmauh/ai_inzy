import React from 'react';
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

const StockChart = ({ data }) => {
  const { t } = useLanguage();
  if (!data || data.length === 0) return <p className="text-center text-gray-500">No data to display</p>;

  // Przygotowanie danych: nałożenie anomalii i sygnałów na wykres cenowy
  // Używamy ComposedChart, aby połączyć linię cen z punktami anomalii (Scatter)
  
  const formattedData = data.map(item => ({
    ...item,
    // Punkty dla anomalii i sygnałów kupna wymagają tych samych współrzędnych X i Y co linia ceny
    anomalyVal: item.is_anomaly ? item.close : null,
    buySignalVal: item.signal === 'Buy' ? item.close : null
  }));

  const CustomArrow = (props) => {
    const { cx, cy } = props;
    if (!cx || !cy) return null;
    return (
      <svg x={cx - 10} y={cy + 10} width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="19" x2="12" y2="5"></line>
        <polyline points="5 12 12 5 19 12"></polyline>
      </svg>
    );
  };

  return (
    <div className="w-full h-[400px] bg-slate-800 p-4 rounded-lg shadow-lg">
      <h3 className="text-lg font-bold text-gray-200 mb-4">{t('charts.priceTitle')}</h3>
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
          <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fill: '#9CA3AF' }}
            tickFormatter={(str) => {
              try {
                return str.split('T')[0];
              } catch { return str; }
            }}
            minTickGap={30}
          />
          <YAxis domain={['auto', 'auto']} tick={{ fill: '#9CA3AF' }} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }}
            itemStyle={{ color: '#F3F4F6' }}
            labelStyle={{ color: '#9CA3AF' }}
          />
          <Legend />
          
          {/* Główna linia ceny */}
          <Line 
            type="monotone" 
            dataKey="close" 
            stroke="#3B82F6" 
            dot={false} 
            name={t('charts.closePrice')}
            strokeWidth={2}
          />

          {/* Punkty anomalii */}
          <Scatter 
            name={t('charts.anomaly')}
            dataKey="anomalyVal" 
            fill="#EF4444" 
            shape="circle"
          />

          {/* Strzałki sygnałów kupna */}
          <Scatter 
            name={t('charts.buySignal')}
            dataKey="buySignalVal" 
            shape={<CustomArrow />}
            legendType="triangle"
            fill="#10B981"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;
