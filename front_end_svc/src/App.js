import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import SaaSPage from './components/SaaSPage';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  return (
    <div className="app">
      {currentPage === 'landing' && (
        <LandingPage onGetStarted={() => navigateTo('saas')} />
      )}
      {currentPage === 'saas' && (
        <SaaSPage onBack={() => navigateTo('landing')} />
      )}
      {currentPage === 'dashboard' && (
        <Dashboard onBack={() => navigateTo('landing')} />
      )}
    </div>
  );
}

export default App;
