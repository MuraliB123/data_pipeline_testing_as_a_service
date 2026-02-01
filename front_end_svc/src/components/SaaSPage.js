import React, { useState } from 'react';
import ConnectionsPage from './ConnectionsPage';
import PipelinesPage from './PipelinesPage';

const SaaSPage = ({ onBack }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');

  const jobHistory = [
    { id: 1, name: 'Customer ETL Pipeline', status: 'Completed', time: '2 hours ago', tests: 24, passed: 22, failed: 2 },
    { id: 2, name: 'Sales Data Validation', status: 'Running', time: '15 mins ago', tests: 18, passed: 18, failed: 0 },
    { id: 3, name: 'Inventory Sync Pipeline', status: 'Failed', time: '1 day ago', tests: 31, passed: 28, failed: 3 },
    { id: 4, name: 'Marketing Attribution', status: 'Completed', time: '2 days ago', tests: 15, passed: 15, failed: 0 },
    { id: 5, name: 'Financial Reporting ETL', status: 'Completed', time: '3 days ago', tests: 42, passed: 40, failed: 2 }
  ];

  // Render connections page
  if (currentPage === 'connections') {
    return (
      <ConnectionsPage onBack={() => setCurrentPage('dashboard')} />
    );
  }

  // Render pipelines page
  if (currentPage === 'pipelines') {
    return (
      <PipelinesPage onBack={() => setCurrentPage('dashboard')} />
    );
  }

  return (
    <div className="saas-dashboard">
      {/* Top Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-left">
          <button 
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <div className="logo">
             <span style={{
            fontFamily: 'Inter, Segoe UI, Arial, sans-serif',
            fontWeight: 900,
            fontSize: '1.7rem',
            letterSpacing: '-0.04em',
            background: 'linear-gradient(90deg, #6366f1 0%, #10b981 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            lineHeight: 0.7
          }}>DataPulse AI</span>
          </div>
        </div>
        <div className="nav-right">
          <div className="user-avatar">MB</div>
        </div>
      </nav>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="user-profile">
            <div className="profile-avatar">MB</div>
            <div className="profile-info">
              <h4>Murali B</h4>
              <p>Enterprise Admin</p>
            </div>
          </div>
        </div>
        <nav className="sidebar-nav">
          <a 
            href="#" 
            className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              setCurrentPage('dashboard');
            }}
          >
            <span className="nav-icon">📊</span>
            <span>Dashboard</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">👤</span>
            <span>Profile</span>
          </a>
          <a 
            href="#" 
            className={`nav-item ${currentPage === 'connections' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              setCurrentPage('connections');
            }}
          >
            <span className="nav-icon">🔗</span>
            <span>Connections</span>
          </a>
          <a 
            href="#" 
            className={`nav-item ${currentPage === 'pipelines' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              setCurrentPage('pipelines');
            }}
          >
            <span className="nav-icon">⚙️</span>
            <span>Pipelines</span>
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">❓</span>
            <span>Help</span>
          </a>
          <div className="nav-divider"></div>
          <a href="#" className="nav-item logout" onClick={onBack}>
            <span className="nav-icon">🚪</span>
            <span>Log Out</span>
          </a>
        </nav>
      </aside>

    {/* Main Content */}
        <main className="main-content">
          <div className="content-header">
           <h3 style={{ fontFamily: 'Georgia, serif', fontSize: '2.2rem', fontWeight: '400', letterSpacing: '0.5px', color: '#2c3e50' }}>Selenium for Data Pipelines</h3>
            <button className="btn btn-primary">
            + New Test Job
            </button>
          </div>

          <div className="jobs-overview">
            <div className="overview-card">
            <div className="card-icon success">✅</div>
            <div className="card-content">
              <h3 style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '2rem', fontWeight: '600', color: '#2c3e50' }}>128</h3>
              <p style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '0.875rem', fontWeight: '500', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total Jobs</p>
            </div>
            </div>
            <div className="overview-card">
            <div className="card-icon running">⏳</div>
            <div className="card-content">
              <h3 style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '2rem', fontWeight: '600', color: '#2c3e50' }}>3</h3>
              <p style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '0.875rem', fontWeight: '500', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Running</p>
            </div>
            </div>
            <div className="overview-card">
            <div className="card-icon success">📈</div>
            <div className="card-content">
              <h3 style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '2rem', fontWeight: '600', color: '#2c3e50' }}>94.2%</h3>
              <p style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '0.875rem', fontWeight: '500', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Success Rate</p>
            </div>
            </div>
            <div className="overview-card">
            <div className="card-icon warning">⚠️</div>
            <div className="card-content">
              <h3 style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '2rem', fontWeight: '600', color: '#2c3e50' }}>7</h3>
              <p style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '0.875rem', fontWeight: '500', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Failed Today</p>
            </div>
            </div>
          </div>

          <div className="jobs-table">
            <div className="table-header">
            <h2 style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontSize: '1.5rem', fontWeight: '600', color: '#1e293b' }}>Recent Test Jobs</h2>
            <div className="table-filters">
              <select className="filter-select">
                <option>All Status</option>
                <option>Completed</option>
                <option>Running</option>
                <option>Failed</option>
              </select>
            </div>
            </div>
            
            <div className="table-container">
            <table>
              <thead>
                <tr>
                <th>Pipeline Name</th>
                <th>Status</th>
                <th>Tests Run</th>
                <th>Success Rate</th>
                <th>Last Run</th>
                <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobHistory.map(job => (
                <tr key={job.id}>
                  <td>
                    <div className="job-name" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontWeight: '500', color: '#1e293b' }}>
                    <span className="job-icon">🔄</span>
                    {job.name}
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${job.status.toLowerCase()}`} style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontWeight: '500' }}>
                    {job.status}
                    </span>
                  </td>
                  <td style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontWeight: '400', color: '#475569' }}>{job.tests}</td>
                  <td>
                    <div className="success-rate">
                    <span style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontWeight: '600', color: '#059669' }}>{Math.round((job.passed / job.tests) * 100)}%</span>
                    <div className="rate-bar">
                      <div 
                        className="rate-fill" 
                        style={{width: `${(job.passed / job.tests) * 100}%`}}
                      ></div>
                    </div>
                    </div>
                  </td>
                  <td style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', fontWeight: '400', color: '#64748b' }}>{job.time}</td>
                  <td>
                    <button className="btn-action">View Details</button>
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        </main>

        {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default SaaSPage;
