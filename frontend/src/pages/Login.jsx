import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Droplets, Lock, User } from 'lucide-react';
import axios from 'axios';
import './Auth.css';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
        const response = await axios.post('http://127.0.0.1:8000/api/login/', {
        username: username,
        password: password
      });

      if (response.data.success) {
        const userData = response.data.data;
        // Simpan data aslinya ke localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Langsung arahkan ke dashboard utama
        navigate('/dashboard');
      }
} catch (error) {
       if (error.response && error.response.status === 401) {
         setErrorMsg('Username atau Password salah!');
       } else if (error.response) {
         setErrorMsg(error.response.data.message || 'Login gagal.');
       } else if (error.request) {
         setErrorMsg('Tidak dapat terhubung ke server. Pastikan server berjalan.');
       } else {
         setErrorMsg('Terjadi kesalahan: ' + error.message);
       }
       console.error(error);
     }
  };

  return (
    <div className="auth-container">
      <div className="glass-panel auth-card animate-fade-in">
        <div className="auth-header">
          <div className="logo-icon">
            <Droplets size={32} color="white" />
          </div>
          <h2>Tani Cerdas</h2>
          <p>Masuk ke akun Anda</p>
        </div>

        <form onSubmit={handleLogin} className="auth-form">
          <div className="input-wrapper">
            <User className="input-icon" size={20} />
            <input 
              type="text" 
              placeholder="Username" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="auth-input"
              required
            />
          </div>

          <div className="input-wrapper">
            <Lock className="input-icon" size={20} />
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input"
              required
            />
          </div>

          {errorMsg && <p style={{color: '#ef4444', fontSize: '0.875rem', marginTop: '-0.5rem', marginBottom: '0.5rem'}}>{errorMsg}</p>}

          <button type="submit" className="btn-primary auth-submit">
            Login Sekarang
          </button>
        </form>

        <div className="auth-footer">
          <p>Belum punya akun? <Link to="/register">Daftar di sini</Link></p>
        </div>
      </div>
    </div>
  );
}
