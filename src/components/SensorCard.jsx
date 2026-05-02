import { Activity } from 'lucide-react';
import './Components.css';

export default function SensorCard({ title, value, unit, icon: Icon, color, trend }) {
  return (
    <div className="glass-panel sensor-card animate-fade-in">
      <div className="sensor-header">
        <h3 className="sensor-title">{title}</h3>
        <div className="sensor-icon" style={{ backgroundColor: `${color}20`, color: color }}>
          <Icon size={24} />
        </div>
      </div>
      
      <div className="sensor-body">
        <div className="sensor-value-wrapper">
          <span className="sensor-value">{value}</span>
          <span className="sensor-unit">{unit}</span>
        </div>
        
        {trend && (
          <div className="sensor-trend">
            <Activity size={16} />
            <span>{trend}</span>
          </div>
        )}
      </div>
    </div>
  );
}
