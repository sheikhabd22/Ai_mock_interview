import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Auth from './components/Auth';
import Setup from './components/Setup';
import Interview from './components/Interview';
import Report from './components/Report';
import Loading from './components/Loading';

function AppContent() {
  const { page } = useApp();

  return (
    <div id="app">
      {page === 'auth' && <Auth />}
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
