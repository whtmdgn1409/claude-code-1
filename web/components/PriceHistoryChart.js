'use client';

import { useMemo } from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { currencyKRW } from '@/lib/format';

const parseDate = (value) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date;
};

const toNumber = (value) => {
  const next = Number(value);
  return Number.isFinite(next) ? next : null;
};

const formatPointLabel = (value) => currencyKRW(value);

const formatLabel = (value) => value;

export default function PriceHistoryChart({ rows = [] }) {
  const chartData = useMemo(() => {
    const parsed = rows
      .map((row) => {
        const timestamp = parseDate(row.recorded_at);
        const price = toNumber(row.price);
        const originalPrice = toNumber(row.original_price);
        if (!timestamp || price === null) return null;

        return {
          price,
          original_price: originalPrice,
          recorded_at: timestamp.toISOString(),
          label: `${timestamp.getFullYear()}-${String(timestamp.getMonth() + 1).padStart(2, '0')}-${String(timestamp.getDate()).padStart(2, '0')}`,
        };
      })
      .filter(Boolean)
      .sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime());

    return parsed;
  }, [rows]);

  if (!chartData.length) {
    return (
      <section className="section detail-chart" role="status">
        <strong>가격 이력</strong>
        <p>가격 이력 데이터가 없습니다.</p>
      </section>
    );
  }

  return (
    <section className="section detail-chart">
      <strong>가격 이력</strong>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ left: 12, right: 12, top: 12, bottom: 12 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} />
            <YAxis
              width={58}
              tick={{ fontSize: 11 }}
              tickFormatter={formatPointLabel}
              tickLine={false}
            />
            <Tooltip formatter={formatPointLabel} labelFormatter={formatLabel} />
            <Line
              type="monotone"
              dataKey="price"
              dot={false}
              strokeWidth={2}
              stroke="#111827"
              activeDot={{ r: 4, fill: '#111827' }}
            />
            <Line
              type="monotone"
              dataKey="original_price"
              dot={false}
              stroke="#9ca3af"
              strokeWidth={1}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
