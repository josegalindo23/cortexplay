/**
 * TimeSeries — activation chart for a selected brain region
 * Uses Recharts to display fMRI signal over time
 */
import { LineChart, Line, XAxis, YAxis, ReferenceLine, Tooltip, ResponsiveContainer } from 'recharts'

export default function TimeSeries({ data, currentTime }) {
  if (!data) return (
    <p className="text-gray-600 text-xs">Select a region to see its activation over time</p>
  )

  const chartData = data.timepoints.map((t, i) => ({
    t,
    activation: parseFloat(data.activations[i].toFixed(4))
  }))

  return (
    <ResponsiveContainer width="100%" height={120}>
      <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: -20 }}>
        <XAxis dataKey="t" tick={{ fill: '#555', fontSize: 9 }} tickLine={false} />
        <YAxis tick={{ fill: '#555', fontSize: 9 }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: '#111', border: '1px solid #333', fontSize: 10 }}
          labelFormatter={t => `t=${t}s`}
          formatter={v => [v.toFixed(3), 'activation']}
        />
        <ReferenceLine y={0} stroke="#333" strokeDasharray="3 3" />
        <ReferenceLine x={currentTime} stroke="#f97316" strokeWidth={1.5} />
        <Line
          type="monotone"
          dataKey="activation"
          stroke="#f97316"
          strokeWidth={1.5}
          dot={false}
          activeDot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}