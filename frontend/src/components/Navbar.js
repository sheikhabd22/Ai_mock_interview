import React from 'react';
import { useApp } from '../context/AppContext';

export default function Navbar() {
  const { setPage, logout, token } = useApp();

  return (
    <nav className="navbar">
      <div className="nav-brand" onClick={() => setPage('home')}>
        <span>AI Mock Interview</span>
      </div>
      
      <div className="nav-links">
        <span className="nav-link" onClick={() => setPage('home')}>Home</span>
        
        {token ? (
          <>
            <span className="nav-link" onClick={() => setPage('setup')}>Dashboard</span>
            <button className="btn btn-outline btn-sm" onClick={logout}>Logout</button>
          </>
        ) : (
          <button className="btn btn-primary btn-sm" onClick={() => setPage('auth')}>
            Get Started
          </button>
        )}
      </div>
    </nav>
  );
}
