import React, { useState } from 'react';
import ProgressModal from './ProgressModal';
import ResultsModal from './ResultsModal';

// Default test user data
const defaultUser = {
  name: 'John Doe',
  initials: 'JD',
  role: 'Data Engineer',
  email: 'john.doe@company.com',
  pipelinesCount: 3,
  testsRun: 156
};

// Default pipelines
const defaultPipelines = [
  {
    id: 1,
    name: 'Customer SCD2 Pipeline',
    description: 'Slowly Changing Dimension Type 2 ETL for customer data with company tracking.',
    status: 'active',
    lastRun: '2 hours ago',
    testCases: 20,
    icon: '👥'
  },
  {
    id: 2,
    name: 'Sales Analytics Pipeline',
    description: 'Daily aggregation of sales transactions with regional breakdowns.',
    status: 'active',
    lastRun: '1 day ago',
    testCases: 15,
    icon: '📈'
  },
  {
    id: 3,
    name: 'Inventory Sync Pipeline',
    description: 'Real-time inventory synchronization between warehouse systems.',
    status: 'inactive',
    lastRun: '5 days ago',
    testCases: 12,
    icon: '📦'
  }
];

const Dashboard = ({ onBack }) => {
  const [selectedPipeline, setSelectedPipeline] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  const handlePipelineSelect = (pipeline) => {
    setSelectedPipeline(pipeline.id === selectedPipeline?.id ? null : pipeline);
  };

  const handleTriggerPipeline = async () => {
    if (!selectedPipeline || selectedPipeline.id !== 1) {
      alert('Only Customer SCD2 Pipeline is available for testing.');
      return;
    }

    setIsRunning(true);
    setElapsedTime(0);
    setResults(null);

    // Start timer
    const timerInterval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    try {
      // Call the backend start-signal endpoint
      const response = await fetch('http://localhost:5000/start-signal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      
      clearInterval(timerInterval);
      setIsRunning(false);
      setResults(data);
    } catch (error) {
      clearInterval(timerInterval);
      setIsRunning(false);
      setResults({
        status: 'error',
        message: error.message || 'Failed to connect to the server'
      });
    }
  };

  const handleCloseResults = () => {
    setResults(null);
    setElapsedTime(0);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Home
        </button>
        <div className="logo">
          <div className="logo-icon">🔬</div>
          <span>DataTest Pro</span>
        </div>
      </header>

      <main className="dashboard-content">
        {/* User Profile Card */}
        <div className="user-profile-card">
          <div className="user-avatar">{defaultUser.initials}</div>
          <div className="user-info">
            <h2>{defaultUser.name}</h2>
            <div className="user-role">{defaultUser.role}</div>
            <div className="user-email">{defaultUser.email}</div>
          </div>
          <div className="user-stats">
            <div className="stat-item">
              <div className="stat-value">{defaultUser.pipelinesCount}</div>
              <div className="stat-label">Pipelines</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{defaultUser.testsRun}</div>
              <div className="stat-label">Tests Run</div>
            </div>
          </div>
        </div>

        {/* Pipelines Section */}
        <div className="section-header">
          <h2 className="section-title">Your Pipelines</h2>
        </div>

        <div className="pipelines-grid">
          {defaultPipelines.map(pipeline => (
            <div
              key={pipeline.id}
              className={`pipeline-card ${selectedPipeline?.id === pipeline.id ? 'selected' : ''}`}
              onClick={() => handlePipelineSelect(pipeline)}
            >
              <div className="pipeline-header">
                <div className="pipeline-icon">{pipeline.icon}</div>
                <span className={`pipeline-status status-${pipeline.status}`}>
                  {pipeline.status}
                </span>
              </div>
              <h3 className="pipeline-name">{pipeline.name}</h3>
              <p className="pipeline-desc">{pipeline.description}</p>
              <div className="pipeline-meta">
                <span>🕒 {pipeline.lastRun}</span>
                <span>🧪 {pipeline.testCases} tests</span>
              </div>
            </div>
          ))}
        </div>

        {/* Action Panel */}
        {selectedPipeline && (
          <div className="action-panel">
            <div className="action-info">
              <h3>Ready to Test: {selectedPipeline.name}</h3>
              <p>This will run the complete testing pipeline: Analysis → Test Generation → Execution</p>
            </div>
            <button 
              className="btn btn-trigger"
              onClick={handleTriggerPipeline}
              disabled={selectedPipeline.id !== 1}
            >
              ▶ Run Tests
            </button>
          </div>
        )}
      </main>

      {/* Progress Modal */}
      {isRunning && (
        <ProgressModal elapsedTime={elapsedTime} />
      )}

      {/* Results Modal */}
      {results && (
        <ResultsModal 
          results={results} 
          elapsedTime={elapsedTime}
          onClose={handleCloseResults} 
        />
      )}
    </div>
  );
};

export default Dashboard;
