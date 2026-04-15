import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import {
  createInterview,
  generateQuestions,
  listInterviews,
  uploadResume,
} from '../services/api';

export default function Setup() {
  const {
    setPage, showLoading, hideLoading,
    setInterviewId, setInterviewMeta, setQuestions, setCurrentQuestionIndex,
  } = useApp();

  const [role, setRole] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [interviewType, setInterviewType] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [resumeFile, setResumeFile] = useState(null);
  const [pastInterviews, setPastInterviews] = useState([]);
  const [loadingPast, setLoadingPast] = useState(true);

  useEffect(() => {
    listInterviews()
      .then(setPastInterviews)
      .catch(() => {})
      .finally(() => setLoadingPast(false));
  }, []);

  const handleStart = async (e) => {
    e.preventDefault();
    try {
      showLoading('Setting up interview & generating questions...');

      let resumeText = null;
      if (resumeFile) {
        showLoading('Parsing resume...');
        const parsed = await uploadResume(resumeFile);
        resumeText = parsed.parsed_data.raw_text;
        showLoading('Generating questions based on resume...');
      }

      const interview = await createInterview(role, experienceLevel, interviewType);
      setInterviewId(interview.id);
      setInterviewMeta({ role, experienceLevel, interviewType });

      const qData = await generateQuestions(role, experienceLevel, interviewType, numQuestions, resumeText);
      setQuestions(qData.questions);
      setCurrentQuestionIndex(0);

      hideLoading();
      setPage('interview');
    } catch (err) {
      hideLoading();
      alert('Error: ' + err.message);
    }
  };

  return (
    <div className="container">
      <header className="top-bar">
        <h2>Interview Setup</h2>
      </header>

      <div className="card">
        <form onSubmit={handleStart}>
          <div className="form-group">
            <label>Job Role</label>
            <input
              type="text"
              placeholder="e.g. Software Engineer, Data Scientist"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Experience Level</label>
            <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)} required>
              <option value="">Select level</option>
              <option value="Fresher">Fresher (0-1 years)</option>
              <option value="Junior">Junior (1-3 years)</option>
              <option value="Mid-Level">Mid-Level (3-5 years)</option>
              <option value="Senior">Senior (5-10 years)</option>
              <option value="Lead">Lead (10+ years)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Interview Type</label>
            <select value={interviewType} onChange={(e) => setInterviewType(e.target.value)} required>
              <option value="">Select type</option>
              <option value="Technical">Technical</option>
              <option value="HR">HR / Behavioral</option>
              <option value="Mixed">Mixed</option>
            </select>
          </div>
          <div className="form-group">
            <label>Number of Questions</label>
            <input
              type="number"
              min="1"
              max="10"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value) || 5)}
              required
            />
          </div>
          <div className="form-group">
            <label>Upload Resume (Optional)</label>
            <input
              type="file"
              accept=".txt,.pdf,.doc,.docx"
              onChange={(e) => setResumeFile(e.target.files[0])}
            />
            <small className="muted">We'll tailor your interview to your background!</small>
          </div>
          <button type="submit" className="btn btn-primary">Start Interview</button>
        </form>
      </div>

      <div className="card">
        <h3 className="section-title">Past Sessions</h3>
        {loadingPast ? (
          <p className="muted">Loading sessions...</p>
        ) : pastInterviews.length === 0 ? (
          <p className="muted">No past sessions found.</p>
        ) : (
          <div className="interview-list">
            {pastInterviews.map((iv) => (
              <div key={iv.id} className="interview-item">
                <div className="interview-info">
                  <div className="info">{iv.role}</div>
                  <div className="meta">
                    {iv.interview_type} &middot; {iv.experience_level} &middot; {new Date(iv.date).toLocaleDateString()}
                  </div>
                </div>
                <div className="interview-status">
                  {iv.score !== null ? (
                    <span className="score-badge">{Math.round(iv.score)}</span>
                  ) : (
                    <span className="muted-text">In progress</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
