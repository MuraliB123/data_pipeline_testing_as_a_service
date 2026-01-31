import React from 'react';

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

const ProgressModal = ({ elapsedTime }) => {
  // Determine which step is active based on elapsed time
  const getStepStatus = (stepIndex) => {
    // Rough estimation: Step 1 (0-30s), Step 2 (30-60s), Step 3 (60s+)
    if (elapsedTime < 30) {
      if (stepIndex === 0) return 'active';
      return 'pending';
    } else if (elapsedTime < 60) {
      if (stepIndex === 0) return 'completed';
      if (stepIndex === 1) return 'active';
      return 'pending';
    } else {
      if (stepIndex <= 1) return 'completed';
      return 'active';
    }
  };

  const steps = [
    { name: 'Analyzing ETL Pipeline', desc: 'Generating analysis report...' },
    { name: 'Generating Test Cases', desc: 'Creating quality & scenario checks...' },
    { name: 'Executing Tests', desc: 'Running validations...' }
  ];

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="progress-spinner">
          <div className="spinner-ring"></div>
        </div>
        
        <h2 className="progress-title">Pipeline Running</h2>
        <p className="progress-subtitle">Please wait while we test your pipeline...</p>
        
        <div className="progress-timer">{formatTime(elapsedTime)}</div>
        
        <div className="progress-steps">
          {steps.map((step, index) => {
            const status = getStepStatus(index);
            return (
              <div key={index} className={`step-item ${status}`}>
                <div className="step-icon">
                  {status === 'completed' ? '✓' : index + 1}
                </div>
                <div>
                  <div>{step.name}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ProgressModal;
