import React from 'react';
import { useApp } from '../context/AppContext';

export default function Home() {
  const { setPage, token } = useApp();

  return (
    <div className="home-container">
      <section className="hero">
        <h1>Practice Interviews at the Speed of Thought.</h1>
        <p>
          Master your next technical or behavioral interview with our context-aware AI. 
          Real-time voice evaluation, personalized feedback, and resume-based tailoring.
        </p>
        <div className="hero-actions">
          <button 
            className="btn btn-primary" 
            style={{ width: 'auto', padding: '0.75rem 2rem', fontSize: '1rem' }}
            onClick={() => setPage(token ? 'setup' : 'auth')}
          >
            Start Practice Now
          </button>
        </div>

        <div className="feature-grid">
          <div className="feature-card">
            <h4>Voice Native</h4>
            <p>Speak naturally. Our AI evaluates your tone, clarity, and technical accuracy in real-time.</p>
          </div>
          <div className="feature-card">
            <h4>Context Aware</h4>
            <p>Upload your resume to receive highly relevant questions tailored to your specific background.</p>
          </div>
          <div className="feature-card">
            <h4>Instant Insight</h4>
            <p>Get a detailed breakdown of your strengths and weaknesses immediately after each session.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
