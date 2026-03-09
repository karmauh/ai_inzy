import React from 'react';
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

const TechnicalCharts = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
      {/* 1. Wykres RSI */}
      <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-purple-400">RSI (14)</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" hide />
              <YAxis domain={[0, 100]} stroke="#9CA3AF" />
              <Tooltip 
                 contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#F3F4F6' }}
                 labelStyle={{ color: '#9CA3AF' }}
              />
              <ReferenceLine y={70} stroke="red" strokeDasharray="3 3" />
              <ReferenceLine y={30} stroke="green" strokeDasharray="3 3" />
              <Line type="monotone" dataKey="rsi" stroke="#8884d8" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Wykres MACD */}
      <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-blue-400">MACD (12, 26, 9)</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" hide />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                 contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#F3F4F6' }}
                 labelStyle={{ color: '#9CA3AF' }}
              />
              <ReferenceLine y={0} stroke="#6B7280" />
              <Line type="monotone" dataKey="macd" stroke="#60A5FA" dot={false} strokeWidth={2} name="MACD" />
              <Line type="monotone" dataKey="macd_signal" stroke="#F87171" dot={false} strokeWidth={2} name="Signal" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Wstęgi Bollingera i EMA */}
      <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-green-400">Bollinger Bands & EMA</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" hide />
              <YAxis domain={['auto', 'auto']} stroke="#9CA3AF" />
              <Tooltip 
                 contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#F3F4F6' }}
                 labelStyle={{ color: '#9CA3AF' }}
                 formatter={(value) => value?.toFixed(2)}
              />
              <Area type="monotone" dataKey="bb_upper" stroke="none" fill="#10B981" fillOpacity={0.1} />
              <Area type="monotone" dataKey="bb_lower" stroke="none" fill="#10B981" fillOpacity={0.1} />
              <Line type="monotone" dataKey="close" stroke="#FFFFFF" dot={false} strokeWidth={1} name="Price" />
              <Line type="monotone" dataKey="ema_20" stroke="#FBBF24" dot={false} strokeWidth={1} name="EMA 20" />
              <Line type="monotone" dataKey="ema_50" stroke="#F472B6" dot={false} strokeWidth={1} name="EMA 50" />
              {/* Dodatkowe rysowanie wstęg jako linii dla lepszej widoczności */}
              <Line type="monotone" dataKey="bb_upper" stroke="#10B981" dot={false} strokeWidth={1} strokeDasharray="2 2" name="BB Upper" />
              <Line type="monotone" dataKey="bb_lower" stroke="#10B981" dot={false} strokeWidth={1} strokeDasharray="2 2" name="BB Lower" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. ATR / Zmienność */}
      <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-bold mb-4 text-pink-400">Volatility (ATR & StdDev)</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" hide />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                 contentStyle={{ backgroundColor: '#1F2937', border: 'none', color: '#F3F4F6' }}
                 labelStyle={{ color: '#9CA3AF' }}
              />
              <Line type="monotone" dataKey="atr" stroke="#EC4899" dot={false} strokeWidth={2} name="ATR (14)" />
              <Line type="monotone" dataKey="volatility" stroke="#9CA3AF" dot={false} strokeWidth={1} strokeDasharray="3 3" name="StdDev (20)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default TechnicalCharts;
