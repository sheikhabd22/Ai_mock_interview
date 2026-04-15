import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { transcribeAudio, evaluateAnswer, speakText } from '../services/api';

export default function Interview() {
  const {
    questions, currentQuestionIndex, setCurrentQuestionIndex,
    interviewId, showLoading, hideLoading, setPage,
  } = useApp();

  const [isRecording, setIsRecording] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [phase, setPhase] = useState('record'); // record | transcript | evaluation

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const total = questions.length;
  const currentQ = questions[currentQuestionIndex] || 'No question';

  // Reset state when question changes
  useEffect(() => {
    setPhase('record');
    setTranscript('');
    setEvaluation(null);
    setTimerSeconds(0);
    setIsRecording(false);
    
    // Speak the new question
    if (currentQ && currentQ !== 'No question') {
      speakText(currentQ).catch(err => console.error("TTS failed", err));
    }
  }, [currentQuestionIndex, currentQ]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        handleRecordingComplete();
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setTimerSeconds(0);

      timerRef.current = setInterval(() => {
        setTimerSeconds((s) => s + 1);
      }, 1000);
    } catch {
      alert('Microphone access denied. Please allow microphone access.');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    clearInterval(timerRef.current);
  }, []);

  const handleRecordingComplete = async () => {
    const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    try {
      showLoading('Transcribing your answer...');
      const result = await transcribeAudio(blob);
      hideLoading();
      setTranscript(result.transcript);
      setPhase('transcript');
    } catch (err) {
      hideLoading();
      alert('Transcription failed: ' + err.message);
    }
  };

  const handleSubmitAnswer = async () => {
    try {
      showLoading('AI is evaluating your answer...');
      const result = await evaluateAnswer(interviewId, currentQ, transcript);
      hideLoading();
      setEvaluation(result);
      setPhase('evaluation');
    } catch (err) {
      hideLoading();
      alert('Evaluation failed: ' + err.message);
    }
  };

  const handleNext = () => {
    const isLast = currentQuestionIndex >= total - 1;
    if (isLast) {
      setPage('report');
    } else {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handleReRecord = () => {
    setTranscript('');
    setPhase('record');
  };

  const formatTime = (s) => {
    const mins = String(Math.floor(s / 60)).padStart(2, '0');
    const secs = String(s % 60).padStart(2, '0');
    return `${mins}:${secs}`;
  };

  const progressPct = ((currentQuestionIndex) / total) * 100;

  return (
    <div className="container">
      <header className="top-bar">
        <h2>Interview in Progress</h2>
        <span className="badge">Q {currentQuestionIndex + 1}/{total}</span>
      </header>

      {/* Question Card */}
      <div className="card">
        <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>
          Question {currentQuestionIndex + 1}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p style={{ fontSize: '1.1rem', margin: 0 }}>{currentQ}</p>
          <button 
            className="btn btn-outline" 
            onClick={() => speakText(currentQ)} 
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
            title="Listen to question"
          >
             Speak
          </button>
        </div>
      </div>

      {/* Recording Card */}
      <div className="card">
        <div className="recording-area">
          <button
            className={`btn-record ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={phase === 'evaluation'}
          >
            <span className="record-icon">{isRecording ? '⏹' : '⏺'}</span>
            <span>{isRecording ? 'Stop' : 'Record'}</span>
          </button>

          {isRecording && (
            <div className="recording-indicator">
              <div className="pulse"></div>
              <span>Recording... Click to stop</span>
            </div>
          )}

          <div className="timer">{formatTime(timerSeconds)}</div>
        </div>

        {/* Transcript */}
        {phase === 'transcript' && (
          <div style={{ marginTop: '1rem' }}>
            <h4>📝 Your Transcript:</h4>
            <p className="transcript">{transcript}</p>
            <div className="btn-group">
              <button className="btn btn-primary" onClick={handleSubmitAnswer}>
                Submit Answer
              </button>
              <button className="btn btn-outline" onClick={handleReRecord}>
                Re-record
              </button>
            </div>
          </div>
        )}

        {/* Evaluation */}
        {phase === 'evaluation' && evaluation && (
          <div className="evaluation-section" style={{ marginTop: '1.5rem' }}>
            <h4 className="section-title">Evaluation</h4>
            <div className="scores-grid">
              {[
                { label: 'Technical Accuracy', value: evaluation.technical_accuracy },
                { label: 'Clarity', value: evaluation.clarity },
                { label: 'Completeness', value: evaluation.completeness },
                { label: 'Communication', value: evaluation.communication },
              ].map((s) => (
                <div className="score-item" key={s.label}>
                  <div className="score-value">{s.value.toFixed(1)}</div>
                  <div className="score-label">{s.label}</div>
                </div>
              ))}
            </div>

            <div className="feedback-grid">
              {evaluation.strengths?.length > 0 && (
                <div className="feedback-column">
                  <h5>Strengths</h5>
                  <ul>{evaluation.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              {evaluation.weaknesses?.length > 0 && (
                <div className="feedback-column">
                  <h5>Weaknesses</h5>
                  <ul>{evaluation.weaknesses.map((w, i) => <li key={i}>{w}</li>)}</ul>
                </div>
              )}
            </div>

            <button className="btn btn-primary" onClick={handleNext} style={{ marginTop: '1.5rem' }}>
              {currentQuestionIndex >= total - 1 ? 'End Interview & View Final Report' : 'Proceed to Next Question'}
            </button>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div className="progress-bar" style={{ width: `${progressPct}%` }}></div>
      </div>
    </div>
  );
}
