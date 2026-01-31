import React from 'react';

const LandingPage = ({ onGetStarted }) => {
  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="logo">
          <div className="logo-icon">🔬</div>
          <span>DataTest Pro</span>
        </div>
      </nav>

      <section className="landing-hero">
        <div className="hero-badge">Automated Pipeline Testing</div>
        <h1 className="hero-title">
          Test Your Data Pipelines <span>With Confidence</span>
        </h1>
        <p className="hero-subtitle">
          Automated testing platform for ETL pipelines. Analyze, generate test cases, 
          and validate your data transformations with AI-powered insights.
        </p>
        <div className="hero-cta">
          <button className="btn btn-primary" onClick={onGetStarted}>
            🚀 Get Started
          </button>
          <button className="btn btn-secondary">
            📖 Documentation
          </button>
        </div>
      </section>

      <section className="landing-features">
        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3 className="feature-title">Smart Analysis</h3>
          <p className="feature-desc">
            Automatically analyze your ETL code and data structures to understand transformations.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🧪</div>
          <h3 className="feature-title">Auto Test Generation</h3>
          <p className="feature-desc">
            Generate comprehensive test cases including quality checks and scenario validations.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">✅</div>
          <h3 className="feature-title">Instant Results</h3>
          <p className="feature-desc">
            Execute tests and get detailed reports with pass/fail status and metrics.
          </p>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
