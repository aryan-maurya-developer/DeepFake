// frontend/src/components/Header.js
import React from 'react';
import { Settings, X, Moon, Sun, LogOut } from 'lucide-react';

const Header = ({ 
  showSettings, 
  toggleSettings, 
  darkMode,
  setDarkMode,
  theme,
  setTheme,
  onLogout,
  renderHealthStatus
}) => {
  const accentColor = theme === 'green' ? '#10b981' : '#f97316';
  
  return (
    <header style={{
      background: `linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.7) 100%)`,
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: `1px solid rgba(255, 255, 255, 0.15)`,
      color: 'white',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      transition: 'all 0.3s ease'
    }}>
      {/* Left: Logo and Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <img 
          src="assets/deepfake.png" 
          alt="Logo" 
          style={{ 
            width: '40px', 
            height: '40px', 
            borderRadius: '8px',
            boxShadow: `0 0 20px rgba(${theme === 'green' ? '16, 185, 129' : '249, 115, 22'}, 0.3)`
          }}
        />
        <div>
          <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700' }}>
            DeepFake <span style={{ fontSize: '0.75rem', fontWeight: '400', marginLeft: '0.5rem', color: accentColor }}>Beta</span>
          </h1>
          <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.9 }}>
            Advanced AI Detection
          </p>
        </div>
      </div>

      {/* Right: Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Health Status */}
        {renderHealthStatus && (
          <div style={{ 
            padding: '0.5rem 1rem', 
            borderRadius: '6px', 
            fontSize: '0.85rem', 
            fontWeight: '500',
            background: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.15)'
          }}>
            {renderHealthStatus()}
          </div>
        )}

        {/* Dark Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          style={{
            background: 'rgba(255, 255, 255, 0.15)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white',
            padding: '0.6rem 0.8rem',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease',
            backdropFilter: 'blur(10px)'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.25)';
            e.target.style.borderColor = 'rgba(255, 255, 255, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.15)';
            e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
          }}
          title={darkMode ? 'Light Mode' : 'Dark Mode'}
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* Settings Toggle */}
        <button
          onClick={toggleSettings}
          style={{
            background: showSettings ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.15)',
            border: showSettings ? `1px solid ${accentColor}` : '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white',
            padding: '0.6rem 0.8rem',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease',
            backdropFilter: 'blur(10px)'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.25)';
            e.target.style.borderColor = accentColor;
          }}
          onMouseLeave={(e) => {
            e.target.style.background = showSettings ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.15)';
            e.target.style.borderColor = showSettings ? accentColor : 'rgba(255, 255, 255, 0.2)';
          }}
          title="Settings"
        >
          {showSettings ? <X size={20} /> : <Settings size={20} />}
        </button>

        {/* Logout */}
        <button
          onClick={onLogout}
          style={{
            background: 'rgba(255, 255, 255, 0.15)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white',
            padding: '0.6rem 0.8rem',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease',
            backdropFilter: 'blur(10px)'
          }}
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.25)';
            e.target.style.borderColor = '#ef4444';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.15)';
            e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
          }}
          title="Logout"
        >
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;