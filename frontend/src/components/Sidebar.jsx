import { Link, useLocation } from 'react-router-dom';
import { Droplets, LayoutDashboard, Settings, Users, LogOut } from 'lucide-react';
import { useEffect, useState } from 'react';
import './Components.css';

export default function Sidebar() {
  const location = useLocation();

  const [userRole, setUserRole] = useState('petani');

  useEffect(() => {
    try {
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);
        setUserRole(parsedUser.role || 'petani');
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  const menuItems = [
    {
      path: '/dashboard',
      name: 'Dashboard Petani',
      icon: LayoutDashboard
    }
  ];

  if (userRole === 'admin') {
    menuItems.push({
      path: '/admin-dashboard',
      name: 'Dashboard Admin',
      icon: Users
    });
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Droplets size={24} />
        </div>
        <h2>Tani Cerdas</h2>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <Link 
              key={item.path} 
              to={item.path} 
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <Link to="/login" className="nav-item text-danger">
          <LogOut size={20} />
          <span>Keluar</span>
        </Link>
      </div>
    </div>
  );
}
