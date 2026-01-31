import React from 'react';

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
};

const ResultsModal = ({ results, elapsedTime, onClose }) => {
  const isSuccess = results.status === 'success';
  const summary = results.summary || {};

  return (
    <div className="modal-overlay">
      <div className="modal-content results-modal">
        <div className={`results-icon ${isSuccess ? 'success' : 'error'}`}>
          {isSuccess ? '✓' : '✗'}
        </div>
        
        <h2 className="results-title">
          {isSuccess ? 'Tests Completed!' : 'Error Occurred'}
        </h2>
        <p className="results-subtitle">
          {isSuccess 
            ? results.message 
            : results.message || 'Something went wrong during execution.'}
        </p>
        
        {isSuccess && summary && (
          <>
            <div className="results-summary">
              <div className="summary-card">
                <div className="summary-value total">{summary.total_tests || 0}</div>
                <div className="summary-label">Total Tests</div>
              </div>
              <div className="summary-card">
                <div className="summary-value passed">{summary.passed || 0}</div>
                <div className="summary-label">Passed</div>
              </div>
              <div className="summary-card">
                <div className="summary-value failed">{summary.failed || 0}</div>
                <div className="summary-label">Failed</div>
              </div>
              <div className="summary-card">
                <div className="summary-value rate">{summary.pass_rate || '0%'}</div>
                <div className="summary-label">Pass Rate</div>
              </div>
            </div>
            
            <p className="results-time">
              ⏱️ Completed in {formatTime(elapsedTime)}
            </p>
          </>
        )}
        
        <button className="btn btn-close" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default ResultsModal;
