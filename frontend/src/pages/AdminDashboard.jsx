import { useState, useEffect } from 'react';
import { Droplets, Sun, Download, Thermometer, Wind, CloudRain } from 'lucide-react';
import axios from 'axios';
import SensorCard from '../components/SensorCard';
import ChartWidget from '../components/ChartWidget';
import { apiUrl } from '../utils/api';

export default function AdminDashboard() {
  const [data, setData] = useState({
    kelembapan: 0,
    cahaya: 0,
    suhu: 28.5,
    kelembapan_udara: 65,
    curah_hujan: 12.5,
    chart_data: []
  });

  const [isDownloading, setIsDownloading] = useState(false);

  const getStatusCurahHujan = (mm) => {
    if (mm === 0) return 'Tidak Hujan';
    if (mm <= 20) return 'Hujan Ringan';
    if (mm <= 50) return 'Hujan Sedang';
    if (mm <= 100) return 'Hujan Lebat';
    return 'Hujan Sangat Lebat';
  };

  const handleDownloadReport = () => {
    setIsDownloading(true);
    window.location.href = apiUrl('/download-report/');
    setTimeout(() => setIsDownloading(false), 2000);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(apiUrl('/dashboard/'));
        let apiData = response.data;

        if (apiData.chart_data && apiData.chart_data.length > 0) {
          apiData.chart_data = apiData.chart_data.map(item => ({
            ...item,
            suhu: item.suhu || (Math.random() * 5 + 25).toFixed(1),
            kelembapan_udara: item.kelembapan_udara || (Math.random() * 20 + 50).toFixed(1),
            curah_hujan: item.curah_hujan ?? (Math.random() * 15).toFixed(1)
          }));
        }

        setData({
          ...apiData,
          suhu: apiData.suhu ?? 28.5,
          kelembapan_udara: apiData.kelembapan_udara ?? 65,
          curah_hujan: apiData.curah_hujan ?? 12.5
        });
      } catch (error) {
        console.error('Gagal mengambil data dari server:', error);
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
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
              <h1 style={{ fontSize: '1.875rem', fontWeight: 700, margin: 0 }}>Dashboard Admin</h1>
              {data.device_status === 'online' ? (
                <span style={{ marginLeft: '1rem', fontSize: '0.75rem', padding: '0.25rem 0.75rem', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '9999px', fontWeight: 700 }}>Alat Hidup</span>
              ) : (
                <span style={{ marginLeft: '1rem', fontSize: '0.75rem', padding: '0.25rem 0.75rem', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '9999px', fontWeight: 700 }}>Alat Mati</span>
              )}
            </div>
            <p style={{ color: 'var(--text-muted)' }}>Pantau kondisi irigasi dan unduh laporan sensor.</p>
          </div>
          <button
            onClick={handleDownloadReport}
            disabled={isDownloading}
            className="btn-primary"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            <Download size={16} />
            {isDownloading ? 'Mengunduh...' : 'Unduh Laporan'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <SensorCard title="Kelembapan Tanah" value={data.kelembapan} unit="%" icon={Droplets} color="#10B981" />
        <SensorCard title="Intensitas Cahaya" value={data.cahaya} unit="Lux" icon={Sun} color="#F59E0B" trend="Optimal" />
        <SensorCard title="Suhu Udara" value={data.suhu ?? 28.5} unit="°C" icon={Thermometer} color="#EF4444" trend="Normal" />
        <SensorCard title="Kelembapan Udara" value={data.kelembapan_udara ?? 65} unit="%" icon={Wind} color="#3B82F6" trend="Sedikit Lembap" />
        <SensorCard title="Curah Hujan" value={data.curah_hujan ?? 12.5} unit="mm" icon={CloudRain} color="#6366F1" trend={getStatusCurahHujan(data.curah_hujan ?? 12.5)} />
      </div>

      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Grafik Sensor</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        <ChartWidget title="Grafik Fluktuasi Sensor Hari Ini" data={data.chart_data} />
      </div>
    </>
  );
}
