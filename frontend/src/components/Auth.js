import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { loginUser, registerUser, setToken as saveToken } from '../services/api';

export default function Auth() {
  const { setToken, setPage, showLoading, hideLoading } = useApp();
  const [activeTab, setActiveTab] = useState('login');
  const [error, setError] = useState('');

  // Login state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register state
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      showLoading('Logging in...');
      const data = await loginUser(loginEmail, loginPassword);
      saveToken(data.access_token);
      setToken(data.access_token);
      hideLoading();
      setPage('setup');
    } catch (err) {
      hideLoading();
      setError(err.message);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      showLoading('Creating account...');
      await registerUser(regName, regEmail, regPassword);
      const data = await loginUser(regEmail, regPassword);
      saveToken(data.access_token);
      setToken(data.access_token);
      hideLoading();
      setPage('setup');
    } catch (err) {
      hideLoading();
      setError(err.message);
    }
  };

  return (
    <div className="container">
      <h1>🎤🤖 AI Voice Mock Interview</h1>
      <p className="subtitle">Practice interviews with AI-powered voice evaluation</p>

      <div className="card">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => { setActiveTab('login'); setError(''); }}
          >
            Login
          </button>
          <button
            className={`tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => { setActiveTab('register'); setError(''); }}
          >
            Register
          </button>
        </div>

        {activeTab === 'login' && (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                placeholder="your@email.com"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">Login</button>
          </form>
        )}

        {activeTab === 'register' && (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                placeholder="John Doe"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                placeholder="your@email.com"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Min 6 characters"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">Register</button>
          </form>
        )}

        {error && <div className="error-msg">{error}</div>}
      </div>
    </div>
  );
}
