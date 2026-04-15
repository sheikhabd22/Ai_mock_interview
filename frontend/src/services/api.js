/**
 * API service for communicating with the backend.
 */

const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('token');
}

export function setToken(token) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
}

export function hasToken() {
  return !!getToken();
}

async function request(url, options = {}) {
  const headers = { ...options.headers };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
}

// ── Auth ─────────────────────────────────────
export async function registerUser(name, email, password) {
  return request('/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  });
}

export async function loginUser(email, password) {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

// ── Interviews ───────────────────────────────
export async function createInterview(role, experience_level, interview_type) {
  return request('/interviews', {
    method: 'POST',
    body: JSON.stringify({ role, experience_level, interview_type }),
  });
}

export async function listInterviews() {
  return request('/interviews');
}

// ── Questions & Resume ───────────────────────
export async function generateQuestions(role, experience_level, interview_type, num_questions, resume_text = null) {
  return request('/generate-questions', {
    method: 'POST',
    body: JSON.stringify({ role, experience_level, interview_type, num_questions, resume_text }),
  });
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  return request('/upload-resume', {
    method: 'POST',
    body: formData,
  });
}

// ── Transcription ────────────────────────────
export async function transcribeAudio(blob) {
  const formData = new FormData();
  formData.append('file', blob, 'recording.webm');
  return request('/transcribe', {
    method: 'POST',
    body: formData,
  });
}

// ── Evaluation ───────────────────────────────
export async function evaluateAnswer(interview_id, question, transcript_text) {
  return request('/evaluate', {
    method: 'POST',
    body: JSON.stringify({ interview_id, question, transcript_text }),
  });
}

// ── Report ───────────────────────────────────
export async function getFinalReport(interview_id) {
  return request(`/final-report/${interview_id}`);
}

// ── Text-to-Speech ───────────────────────────
export async function speakText(text) {
  const res = await fetch(`${API_BASE}/speak`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    throw new Error('TTS request failed');
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  return audio.play();
}
