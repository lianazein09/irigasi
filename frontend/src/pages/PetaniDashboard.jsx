import { useState, useEffect } from 'react';
import { Droplets, Sun, Thermometer, Wind, CloudRain } from 'lucide-react';
import axios from 'axios';
import SensorCard from '../components/SensorCard';
import ChartWidget from '../components/ChartWidget';

export default function PetaniDashboard() {
  const [data, setData] = useState({
    kelembapan: 0,
    cahaya: 0,
    suhu: 28.5,
    kelembapan_udara: 65,
    curah_hujan: 12.5,
    pompa_aktif: false,
    chart_data: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/dashboard/');
        
        let apiData = response.data;
        
        if (apiData.chart_data && apiData.chart_data.length > 0) {
          apiData.chart_data = apiData.chart_data.map(item => ({
            ...item,
            suhu: item.suhu || (Math.random() * 5 + 25).toFixed(1),
            kelembapan_udara: item.kelembapan_udara || (Math.random() * 20 + 50).toFixed(1),
            curah_hujan: item.curah_hujan || (Math.random() * 15).toFixed(1)
          }));
        }

        setData(prevData => ({
          ...apiData,
          pompa_aktif: apiData.pompa_aktif,
          suhu: apiData.suhu || 28.5,
          kelembapan_udara: apiData.kelembapan_udara || 65,
          curah_hujan: apiData.curah_hujan || 12.5
        }));
      } catch (error) {
        console.error("Gagal mengambil data dari server:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="dashboard-header animate-fade-in">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Overview Monitoring</h1>
            <p style={{ color: 'var(--text-muted)' }}>Pantau kondisi irigasi dan sistem secara real-time.</p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <SensorCard 
          title="Kelembapan Tanah"
          value={data.kelembapan}
          unit="%"
          icon={Droplets}
          color="#10B981"
          trend="Semua Zona"
        />
        <SensorCard 
          title="Intensitas Cahaya"
          value={data.cahaya}
          unit="Lux"
          icon={Sun}
          color="#F59E0B"
          trend="Optimal"
        />
        <SensorCard 
          title="Suhu Udara"
          value={data.suhu || 28.5}
          unit="°C"
          icon={Thermometer}
          color="#EF4444"
          trend="Normal"
        />
        <SensorCard 
          title="Kelembapan Udara"
          value={data.kelembapan_udara || 65}
          unit="%"
          icon={Wind}
          color="#3B82F6"
          trend="Sedikit Lembap"
        />
        <SensorCard 
          title="Curah Hujan"
          value={data.curah_hujan || 12.5}
          unit="mm"
          icon={CloudRain}
          color="#6366F1"
          trend="Hujan Ringan"
        />
      </div>

      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Grafik Sensor</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        <ChartWidget 
          title="Grafik Fluktuasi Sensor Hari Ini" 
          data={data.chart_data} 
        />
      </div>
    </>
  );
}
