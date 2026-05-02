import React from 'react';
import { Droplets, Sun, Power, Thermometer, Wind, CloudRain } from 'lucide-react';
import './Components.css';

export default function ZoneCard({ title, moisture, light, suhu, kelembapan_udara, curah_hujan, isValveOn }) {
  // Setup for SVG Circular Progress
  const radius = 60;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  // Membatasi kelembapan maksimal 100%
  const safeMoisture = Math.min(Math.max(moisture, 0), 100);
  const strokeDashoffset = circumference - (safeMoisture / 100) * circumference;

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', overflow: 'hidden' }}>
      <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-main)', margin: 0, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        {title}
      </h3>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.5rem', flexWrap: 'wrap' }}>
        
        {/* Circular Progress Bar */}
        <div style={{ position: 'relative', width: '120px', height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg height="120" width="120" style={{ transform: 'rotate(-90deg)' }}>
            <circle
              stroke="var(--border-color)"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx="60"
              cy="60"
            />
            <circle
              stroke="#10B981"
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease-in-out' }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx="60"
              cy="60"
            />
          </svg>
          <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Droplets size={20} color="#10B981" style={{ marginBottom: '2px' }} />
            <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: '1' }}>{safeMoisture}%</span>
          </div>
        </div>

        {/* Info Area */}
        <div style={{ flex: 1, minWidth: '200px', marginLeft: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '0.4rem', borderRadius: '50%' }}>
              <Sun size={16} color="#F59E0B" />
            </div>
            <div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>Cahaya</p>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>{light} Lux</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '0.4rem', borderRadius: '50%' }}>
              <Thermometer size={16} color="#EF4444" />
            </div>
            <div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>Suhu</p>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>{suhu} °C</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '0.4rem', borderRadius: '50%' }}>
              <Wind size={16} color="#3B82F6" />
            </div>
            <div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>Kel. Udara</p>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>{kelembapan_udara} %</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '0.4rem', borderRadius: '50%' }}>
              <CloudRain size={16} color="#6366F1" />
            </div>
            <div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>Hujan</p>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>{curah_hujan} mm</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', gridColumn: 'span 2' }}>
            <div style={{ background: isValveOn ? 'rgba(59, 130, 246, 0.1)' : 'rgba(239, 68, 68, 0.1)', padding: '0.4rem', borderRadius: '50%' }}>
              <Power size={16} color={isValveOn ? "#3B82F6" : "#EF4444"} />
            </div>
            <div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>Katup Irigasi</p>
              <p style={{ fontSize: '0.8rem', fontWeight: 600, color: isValveOn ? '#3B82F6' : '#EF4444', margin: 0 }}>
                {isValveOn ? 'ON (Menyiram)' : 'OFF (Mati)'}
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
