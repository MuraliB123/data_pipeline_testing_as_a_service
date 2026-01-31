import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  return (
    <div className="app">
      {currentPage === 'landing' && (
        <LandingPage onGetStarted={() => navigateTo('dashboard')} />
      )}
      {currentPage === 'dashboard' && (
        <Dashboard onBack={() => navigateTo('landing')} />
      )}
    </div>
  );
}

export default App;
