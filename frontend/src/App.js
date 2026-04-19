import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Auth from './components/Auth';
import Setup from './components/Setup';
import Interview from './components/Interview';
import Report from './components/Report';
import Loading from './components/Loading';
import Home from './components/Home';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';

import SoftAurora from './components/SoftAurora';

function AppContent() {
  const { page } = useApp();

  return (
    <div id="app">
      <SoftAurora
        speed={0.3}
        scale={1.5}
        brightness={2.2}
        color1="#f8fafc"
        color2="#8b5cf6"
      />
      <Navbar />
      {page === 'home' && <Home />}
      {page === 'auth' && <Auth />}
      {page === 'dashboard' && <Dashboard />}
      {page === 'setup' && <Setup />}
      {page === 'interview' && <Interview />}
      {page === 'report' && <Report />}
      <Loading />
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
