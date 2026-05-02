import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import './Components.css';

export default function ChartWidget({ title, data }) {
  return (
    <div className="glass-panel chart-widget animate-fade-in">
      <div className="chart-header">
        <h3>{title}</h3>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
            <XAxis dataKey="time" stroke="var(--text-muted)" />
            <YAxis yAxisId="left" stroke="var(--text-muted)" domain={[0, 100]} />
            <YAxis yAxisId="right" orientation="right" stroke="var(--text-muted)" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'var(--bg-surface)', 
                borderColor: 'var(--border-light)',
                borderRadius: '8px',
                color: 'var(--text-main)',
                boxShadow: 'var(--shadow-md)'
              }} 
            />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="kelembapan" stroke="var(--color-primary)" strokeWidth={3} activeDot={{ r: 8 }} name="Kelembapan Tanah (%)" />
            <Line yAxisId="right" type="monotone" dataKey="cahaya" stroke="#F59E0B" strokeWidth={3} name="Intensitas Cahaya (Lux)" />
            <Line yAxisId="left" type="monotone" dataKey="suhu" stroke="#EF4444" strokeWidth={3} name="Suhu (°C)" />
            <Line yAxisId="left" type="monotone" dataKey="kelembapan_udara" stroke="#3B82F6" strokeWidth={3} name="Kelembapan Udara (%)" />
            <Line yAxisId="left" type="monotone" dataKey="curah_hujan" stroke="#8B5CF6" strokeWidth={3} name="Curah Hujan (mm)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
