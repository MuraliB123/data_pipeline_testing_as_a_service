import React from 'react';

const LandingPage = ({ onGetStarted }) => {
  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="logo">
          <span style={{
            fontFamily: 'Inter, Segoe UI, Arial, sans-serif',
            fontWeight: 900,
            fontSize: '2.1rem',
            letterSpacing: '-0.04em',
            background: 'linear-gradient(90deg, #6366f1 0%, #10b981 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            lineHeight: 1.1
          }}>DataPulse AI</span>
        </div>
        <div className="nav-actions">
          <button className="btn btn-ghost">Sign In</button>
          <button className="btn btn-primary" onClick={onGetStarted}>Get Started</button>
        </div>
      </nav>

      <section className="enterprise-hero">
        <div className="hero-content">
          <div className="hero-badge">
             Transforming Data Testing with Intelligent Automation
          </div>
          <h1 className="enterprise-title">
            Enterprise-Grade <span className="gradient-text">Data Pipeline Testing</span> at Scale
          </h1>
          <p className="enterprise-subtitle">
            Transform your data operations with DataPulse's AI-powered testing platform. 
            Built for enterprises to ensure data quality, compliance, and operational excellence.
          </p>
          <div className="cta-section">
            <button className="btn btn-primary-large" onClick={onGetStarted}>
              Start Free Enterprise Trial
              <span className="btn-arrow">→</span>
            </button>
            <div className="trial-info">
              <span>✓ 30-day free trial</span>
              <span>✓ No credit card required</span>
              <span>✓ Full enterprise features</span>
            </div>
          </div>
        </div>
        <div className="hero-metrics">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">99.9%</div>
              <div className="metric-label">Data Accuracy</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">85%</div>
              <div className="metric-label">Faster Deployment</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">60%</div>
              <div className="metric-label">Lower Costs</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">24/7</div>
              <div className="metric-label">Enterprise Support</div>
            </div>
          </div>
        </div>
      </section>

      <section className="enterprise-stats">
        <div className="stats-container">
          <div className="stat-item">
            <div className="stat-number">98%</div>
            <div className="stat-desc">Reduction in data incidents</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">75%</div>
            <div className="stat-desc">Faster time-to-market</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">60%</div>
            <div className="stat-desc">Lower operational costs</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">24/7</div>
            <div className="stat-desc">Enterprise support</div>
          </div>
        </div>
      </section>

      <section className="enterprise-features">
        <div className="features-header">
          <h2 className="features-title">AI-Powered Automation at Scale</h2>
          <p className="features-subtitle">Transform your data testing workflow with intelligent automation</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3 className="feature-title">AI-Driven Code Analysis</h3>
            <p className="feature-desc">
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Intelligent Test Automation</h3>
            <p className="feature-desc">
             </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3 className="feature-title">Real-Time Analytics & Insights</h3>
            <p className="feature-desc">
             </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
