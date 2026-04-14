import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { getFinalReport } from '../services/api';

export default function Report() {
  const {
    interviewId, showLoading, hideLoading, setPage,
    setInterviewId, setQuestions, setCurrentQuestionIndex,
  } = useApp();

  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!interviewId) return;
    let cancelled = false;

    const fetchReport = async () => {
      try {
        showLoading('Generating your performance report...');
        const data = await getFinalReport(interviewId);
        if (!cancelled) {
          setReport(data);
          hideLoading();
        }
      } catch (err) {
        if (!cancelled) {
          hideLoading();
          setError(err.message);
        }
      }
    };

    fetchReport();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interviewId]);

  const handleNewInterview = () => {
    setInterviewId(null);
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setPage('setup');
  };

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <p className="error-msg">{error}</p>
          <button className="btn btn-primary" onClick={handleNewInterview} style={{ marginTop: '1rem' }}>
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container">
        <p className="muted">Loading report...</p>
      </div>
    );
  }

  const score = Math.round(report.overall_score);

  return (
    <div className="container">
      <header className="top-bar">
        <h2>📈 Performance Report</h2>
      </header>

      <div className="card report-card">
        {/* Score Circle */}
        <div className="report-score-circle">
          <span className="score-value">{score}</span>
          <span className="score-label">/ 100</span>
        </div>

        {/* Meta */}
        <div className="report-meta">
          <strong>{report.role}</strong> &middot; {report.experience_level} &middot; {report.interview_type}
          <br />
          {report.total_questions} questions answered
        </div>

        {/* Strengths */}
        <div className="report-section">
          <h3>✅ Strengths</h3>
          <ul>
            {(report.strengths || []).map((s, i) => <li key={i}>{s}</li>)}
            {(!report.strengths || report.strengths.length === 0) && <li>N/A</li>}
          </ul>
        </div>

        {/* Weaknesses */}
        <div className="report-section">
          <h3>⚠️ Weaknesses</h3>
          <ul>
            {(report.weaknesses || []).map((w, i) => <li key={i}>{w}</li>)}
            {(!report.weaknesses || report.weaknesses.length === 0) && <li>N/A</li>}
          </ul>
        </div>

        {/* Suggestions */}
        <div className="report-section">
          <h3>💡 Suggestions</h3>
          <ul>
            {(report.suggestions || []).map((s, i) => <li key={i}>{s}</li>)}
            {(!report.suggestions || report.suggestions.length === 0) && <li>N/A</li>}
          </ul>
        </div>

        {/* Question-wise Breakdown */}
        <div className="report-section">
          <h3>📝 Question-wise Breakdown</h3>
          {(report.answers || []).map((ans, i) => (
            <div key={i} className="answer-breakdown">
              <div className="q-header">Q{i + 1}: {ans.question}</div>
              <div className="q-score">
                {ans.evaluation_score !== null ? `${ans.evaluation_score.toFixed(1)}/10` : 'N/A'}
              </div>
              <div className="muted" style={{ marginTop: '0.25rem' }}>
                {ans.transcript_text || 'No transcript'}
              </div>
            </div>
          ))}
        </div>

        <button className="btn btn-primary" onClick={handleNewInterview}>
          Start New Interview
        </button>
      </div>
    </div>
  );
}
