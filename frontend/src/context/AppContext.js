import React, { createContext, useState, useContext, useCallback } from 'react';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [token, setTokenState] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Processing...');
   const [page, setPage] = useState('home');

  // Interview state
  const [interviewId, setInterviewId] = useState(null);
  const [interviewMeta, setInterviewMeta] = useState({});
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const setToken = useCallback((t) => {
    if (t) {
      localStorage.setItem('token', t);
    } else {
      localStorage.removeItem('token');
    }
    setTokenState(t);
  }, []);

  const showLoading = useCallback((text = 'Processing...') => {
    setLoadingText(text);
    setLoading(true);
  }, []);

  const hideLoading = useCallback(() => {
    setLoading(false);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setPage('auth');
  }, [setToken]);

  const value = {
    token, setToken,
    loading, loadingText, showLoading, hideLoading,
    page, setPage,
    interviewId, setInterviewId,
    interviewMeta, setInterviewMeta,
    questions, setQuestions,
    currentQuestionIndex, setCurrentQuestionIndex,
    logout,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  return useContext(AppContext);
}
