import React from 'react';
import { useApp } from '../context/AppContext';

export default function Loading() {
  const { loading, loadingText } = useApp();

  if (!loading) return null;

  return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>{loadingText}</p>
    </div>
  );
}
