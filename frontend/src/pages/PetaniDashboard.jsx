import { useState, useEffect } from 'react';
import { Droplets, Sun, Download, Thermometer, Wind, CloudRain, Power, Settings } from 'lucide-react';
import axios from 'axios';
import SensorCard from '../components/SensorCard';
import ChartWidget from '../components/ChartWidget';
import ZoneCard from '../components/ZoneCard';

export default function PetaniDashboard() {
  const [data, setData] = useState({
    kelembapan: 0,
    cahaya: 0,
    suhu: 28.5, // Mock data
    kelembapan_udara: 65, // Mock data
    curah_hujan: 12.5, // Mock data
    pompa_aktif: false,
    chart_data: []
  });

  const [isDownloading, setIsDownloading] = useState(false);
  const [batasKelembapan, setBatasKelembapan] = useState(40); 

  const handleTogglePompa = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/toggle-pump/');
      if (response.data.success) {
        setData(prev => ({ ...prev, pompa_aktif: response.data.pompa_aktif }));
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Gagal toggle pompa:', error);
      alert('Gagal mengubah status pompa. Silakan coba lagi.');
    }
  };

  const handleSimpanBatas = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/threshold/', {
        batas_kelembapan: batasKelembapan
      });
      if (response.data.success) {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Gagal menyimpan batas:', error);
      alert('Gagal menyimpan ambang batas. Silakan coba lagi.');
    }
  };

  const handleDownloadReport = () => {
    setIsDownloading(true);
    // Mengunduh langsung dari endpoint backend
    window.location.href = 'http://127.0.0.1:8000/api/download-report/';
    setTimeout(() => setIsDownloading(false), 2000); // Reset button state after a short delay
  };

  useEffect(() => {
    const fetchThreshold = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/threshold/');
        if (response.data.batas_kelembapan) {
          setBatasKelembapan(response.data.batas_kelembapan);
        }
      } catch (error) {
        console.error("Gagal mengambil data threshold:", error);
      }
    };

    // Memanggil API backend
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/dashboard/');
        
        let apiData = response.data;
        
        // Mock data untuk metrik baru jika backend belum support
        if (apiData.chart_data && apiData.chart_data.length > 0) {
          apiData.chart_data = apiData.chart_data.map(item => ({
            ...item,
            suhu: item.suhu || (Math.random() * 5 + 25).toFixed(1), // Mock suhu 25-30
            kelembapan_udara: item.kelembapan_udara || (Math.random() * 20 + 50).toFixed(1), // Mock 50-70%
            curah_hujan: item.curah_hujan || (Math.random() * 15).toFixed(1) // Mock 0-15mm
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

    fetchThreshold();
    fetchData();
    // Opsional: Polling setiap 30 detik untuk real-time update
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="dashboard-header animate-fade-in">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Overview Monitoring</h1>
            <p style={{ color: 'var(--text-muted)' }}>Pantau kondisi keseluruhan dan status tiap zona irigasi Kangkung secara real-time.</p>
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

      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Monitoring Per Zona (Kangkung)</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Mocking 3 Zona Kangkung. Idealnya ini dari backend. */}
        <ZoneCard 
          title="Zona 1 - Tunas Kangkung"
          moisture={data.kelembapan ? data.kelembapan - 5 : 42} 
          light={data.cahaya ? data.cahaya + 100 : 1200}
          suhu={data.suhu ? (data.suhu - 0.5).toFixed(1) : 28.0}
          kelembapan_udara={data.kelembapan_udara ? data.kelembapan_udara + 2 : 67}
          curah_hujan={data.curah_hujan || 12.5}
          isValveOn={data.pompa_aktif}
        />
        <ZoneCard 
          title="Zona 2 - Masa Pertumbuhan"
          moisture={data.kelembapan ? data.kelembapan + 8 : 65} 
          light={data.cahaya ? data.cahaya - 50 : 1050}
          suhu={data.suhu ? (data.suhu + 0.2).toFixed(1) : 28.7}
          kelembapan_udara={data.kelembapan_udara ? data.kelembapan_udara - 1 : 64}
          curah_hujan={data.curah_hujan || 12.5}
          isValveOn={false}
        />
        <ZoneCard 
          title="Zona 3 - Siap Panen"
          moisture={data.kelembapan ? data.kelembapan : 55} 
          light={data.cahaya ? data.cahaya + 200 : 1400}
          suhu={data.suhu ? (data.suhu - 0.2).toFixed(1) : 28.3}
          kelembapan_udara={data.kelembapan_udara ? data.kelembapan_udara + 1 : 66}
          curah_hujan={data.curah_hujan || 12.5}
          isValveOn={data.pompa_aktif}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        <ChartWidget 
          title="Grafik Fluktuasi Sensor Hari Ini" 
          data={data.chart_data} 
        />
      </div>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '1rem' }}>Kontrol & Konfigurasi Sistem</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        
        {/* Kontrol Manual */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>
            <Power size={20} color="var(--color-primary)" />
            <h3 style={{ margin: 0, fontSize: '1.125rem' }}>Kontrol Manual Pompa</h3>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Nyalakan atau matikan pompa air secara langsung dari aplikasi.</p>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto', paddingTop: '1rem' }}>
            <div>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Status Saat Ini: </span>
              <strong style={{ color: data.pompa_aktif ? '#3B82F6' : '#EF4444' }}>{data.pompa_aktif ? 'ON' : 'OFF'}</strong>
            </div>
            <button 
              onClick={handleTogglePompa}
              style={{
                backgroundColor: data.pompa_aktif ? '#EF4444' : '#3B82F6',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <Power size={16} />
              {data.pompa_aktif ? 'Matikan Pompa' : 'Nyalakan Pompa'}
            </button>
          </div>
        </div>
      </div>

    </>
  );
}
