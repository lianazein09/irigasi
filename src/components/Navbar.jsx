import { useState, useRef, useEffect } from 'react';
import { Bell, LogOut, ChevronDown, User, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Components.css';

export default function Navbar() {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const [showEditModal, setShowEditModal] = useState(false);
  const [editData, setEditData] = useState({ nama: '', username: '', password: '' });
  const [currentUser, setCurrentUser] = useState({ nama: 'Asep Petani', role: 'petani', username: '' });

  // Ambil data user asli dari localStorage hasil login
  useEffect(() => {
    try {
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);
        setCurrentUser(parsedUser);
        setEditData({ nama: parsedUser.nama, username: parsedUser.username || '', password: '' });
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  const userName = currentUser.nama;
  const userRole = currentUser.role;

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [dropdownRef]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/profile/update/', {
        id_user: currentUser.id_user,
        nama: editData.nama,
        username: editData.username,
        password: editData.password
      });

      if (response.data.success) {
        const updatedUser = response.data.data;
        // Simpan respons dari server ke localStorage
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setCurrentUser(updatedUser);
        setShowEditModal(false);
        alert('Profil berhasil diperbarui!');
      } else {
        alert(response.data.message || 'Gagal memperbarui profil');
      }
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.message || 'Terjadi kesalahan pada server');
    }
  };
  
  return (
    <header className="top-navbar">
      <div className="navbar-search">
        {/* Opsional: Kotak pencarian */}
      </div>

      <div className="navbar-user">
        <button className="btn-secondary" style={{ padding: '0.5rem', border: 'none' }}>
          <Bell size={20} className="text-muted" />
        </button>
        <div 
          className="user-info" 
          ref={dropdownRef}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer', position: 'relative' }}
          onClick={() => setDropdownOpen(!dropdownOpen)}
        >
          <div className="user-details" style={{ textAlign: 'right' }}>
            <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>{userName}</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, textTransform: 'capitalize' }}>{userRole}</p>
          </div>
          <div className="user-avatar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {userName ? userName.charAt(0).toUpperCase() : 'U'}
          </div>
          <ChevronDown size={16} className="text-muted" />

          {dropdownOpen && (
            <div className="dropdown-menu animate-fade-in" style={{
              position: 'absolute', top: '120%', right: '0', backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-color)', borderRadius: '0.5rem',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', minWidth: '150px', padding: '0.5rem', zIndex: 100
            }}>
              <button 
                onClick={() => {
                  setDropdownOpen(false);
                  setShowEditModal(true);
                }}
                style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '0.5rem', 
                  padding: '0.5rem 1rem', border: 'none', background: 'transparent',
                  color: 'var(--text-main)', cursor: 'pointer', borderRadius: '0.25rem', fontWeight: 500, marginBottom: '0.25rem'
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.05)'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <User size={16} />
                <span>Edit Profil</span>
              </button>
              <button 
                onClick={handleLogout}
                style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '0.5rem', 
                  padding: '0.5rem 1rem', border: 'none', background: 'transparent',
                  color: '#EF4444', cursor: 'pointer', borderRadius: '0.25rem', fontWeight: 500
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <LogOut size={16} />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modal Edit Profil */}
      {showEditModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="glass-panel animate-fade-in" style={{
            width: '100%', maxWidth: '400px', padding: '1.5rem', position: 'relative'
          }}>
            <button 
              onClick={() => setShowEditModal(false)}
              style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
            >
              <X size={20} />
            </button>
            
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', color: 'var(--text-main)' }}>Edit Profil</h2>
            
            <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-main)' }}>Nama Lengkap</label>
                <input 
                  type="text" 
                  value={editData.nama}
                  onChange={(e) => setEditData({...editData, nama: e.target.value})}
                  className="auth-input"
                  style={{ width: '100%', padding: '0.75rem' }}
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-main)' }}>Username</label>
                <input 
                  type="text" 
                  value={editData.username}
                  onChange={(e) => setEditData({...editData, username: e.target.value})}
                  className="auth-input"
                  style={{ width: '100%', padding: '0.75rem' }}
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-main)' }}>Password Baru <span style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>(kosongkan jika tidak ingin diubah)</span></label>
                <input 
                  type="password" 
                  value={editData.password}
                  onChange={(e) => setEditData({...editData, password: e.target.value})}
                  className="auth-input"
                  style={{ width: '100%', padding: '0.75rem' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowEditModal(false)} className="btn-secondary" style={{ flex: 1, padding: '0.75rem' }}>
                  Batal
                </button>
                <button type="submit" className="btn-primary" style={{ flex: 1, padding: '0.75rem' }}>
                  Simpan Profil
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
