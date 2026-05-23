import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Droplets, Lock, User, Briefcase, AtSign } from 'lucide-react';
import axios from 'axios';
import './Auth.css';
import { apiUrl } from '../utils/api';

export default function Register() {
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      const response = await axios.post(apiUrl('/register/'), {
        nama: name,
        username: username,
        password: password,
        role: 'user' // Hardcode sebagai Petani
      });

      if (response.data.success) {
        navigate('/login');
      }
    } catch (error) {
      if (error.response && error.response.status === 400) {
        setErrorMsg(error.response.data.message);
      } else {
        setErrorMsg('Terjadi kesalahan koneksi ke server.');
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="glass-panel auth-card animate-fade-in">
        <div className="auth-header">
          <div className="logo-icon">
            <Droplets size={32} color="white" />
          </div>
          <h2>Daftar Akun Baru</h2>
          <p>Bergabung dengan Tani Cerdas</p>
        </div>

        <form onSubmit={handleRegister} className="auth-form">
          <div className="input-wrapper">
            <User className="input-icon" size={20} />
            <input 
              type="text" 
              placeholder="Nama Lengkap" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="auth-input"
              required
            />
          </div>

          <div className="input-wrapper">
            <AtSign className="input-icon" size={20} />
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
            Buat Akun
          </button>
        </form>

        <div className="auth-footer">
          <p>Sudah punya akun? <Link to="/login">Masuk di sini</Link></p>
        </div>
      </div>
    </div>
  );
}
