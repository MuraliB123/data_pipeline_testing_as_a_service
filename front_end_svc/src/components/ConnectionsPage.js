import React, { useState, useEffect } from 'react';

const ConnectionsPage = ({ onBack }) => {
  const [connections, setConnections] = useState([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    type: 'input_sor',
    config: {}
  });

  const connectionTypes = {
    input_sor: { label: 'Flat Files', icon: '📁', color: '#10b981' },
    target_db: { label: 'Destination Databases', icon: '🗄️', color: '#6366f1' },
    api_source: { label: 'API Source Feed', icon: '🔗', color: '#f59e0b' }
  };

  const getConfigFields = (type) => {
    switch (type) {
      case 'input_sor':
        return [
          { key: 'file_path', label: 'File Path', type: 'text', placeholder: 'input_sor/data.csv' },
          { key: 'file_type', label: 'File Type', type: 'select', options: ['csv', 'json', 'xlsx', 'txt'] },
          { key: 'delimiter', label: 'Delimiter', type: 'text', placeholder: ',' },
          { key: 'encoding', label: 'Encoding', type: 'select', options: ['utf-8', 'utf-16', 'ascii'] },
          { key: 'has_header', label: 'Has Header', type: 'checkbox' }
        ];
      case 'target_db':
        return [
          { key: 'host', label: 'Host', type: 'text', placeholder: 'localhost' },
          { key: 'port', label: 'Port', type: 'text', placeholder: '5432' },
          { key: 'database', label: 'Database', type: 'text', placeholder: 'mydb' },
          { key: 'username', label: 'Username', type: 'text', placeholder: 'user' },
          { key: 'password', label: 'Password', type: 'password', placeholder: '••••••••' },
          { key: 'db_type', label: 'Database Type', type: 'select', options: ['postgresql', 'mysql', 'sqlserver', 'oracle'] }
        ];
      case 'api_source':
        return [
          { key: 'base_url', label: 'Base URL', type: 'text', placeholder: 'https://api.example.com' },
          { key: 'auth_type', label: 'Authentication', type: 'select', options: ['none', 'bearer_token', 'api_key', 'basic_auth'] },
          { key: 'auth_value', label: 'Auth Value', type: 'password', placeholder: 'Token/Key/Credentials' },
          { key: 'timeout', label: 'Timeout (seconds)', type: 'text', placeholder: '30' },
          { key: 'rate_limit', label: 'Rate Limit (req/min)', type: 'text', placeholder: '60' }
        ];
      default:
        return [];
    }
  };

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/connections');
      if (response.ok) {
        const data = await response.json();
        setConnections(data.connections || []);
      }
    } catch (error) {
      console.error('Error fetching connections:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:5000/connections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        fetchConnections();
        resetForm();
        setIsFormOpen(false);
      }
    } catch (error) {
      console.error('Error saving connection:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'input_sor',
      config: {}
    });
  };

  const handleInputChange = (key, value, isConfig = false) => {
    if (isConfig) {
      setFormData(prev => ({
        ...prev,
        config: {
          ...prev.config,
          [key]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [key]: value
      }));
    }
  };

  const renderConfigField = (field) => {
    const value = formData.config[field.key] || '';
    
    switch (field.type) {
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleInputChange(field.key, e.target.value, true)}
            className="form-input"
          >
            <option value="">Select {field.label}</option>
            {field.options.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      case 'checkbox':
        return (
          <label className="checkbox-wrapper">
            <input
              type="checkbox"
              checked={value === true}
              onChange={(e) => handleInputChange(field.key, e.target.checked, true)}
              className="form-checkbox"
            />
            <span className="checkbox-label">Enable</span>
          </label>
        );
      default:
        return (
          <input
            type={field.type}
            value={value}
            onChange={(e) => handleInputChange(field.key, e.target.value, true)}
            placeholder={field.placeholder}
            className="form-input"
          />
        );
    }
  };

  const getConnectionStats = () => {
    const stats = {
      total: connections.length,
      input_sor: connections.filter(c => c.type === 'input_sor').length,
      target_db: connections.filter(c => c.type === 'target_db').length,
      api_source: connections.filter(c => c.type === 'api_source').length
    };
    return stats;
  };

  const stats = getConnectionStats();

  return (
    <div className="connections-page">
      {/* Header Section */}
      <div className="connections-header">
        <div className="header-left">
          <button className="back-btn" onClick={onBack}>
            <span>←</span>
            <span>Back to Dashboard</span>
          </button>
          <div className="header-title">
            <h1>Connections</h1>
            <p>Manage your data source and target connections</p>
          </div>
        </div>
        <button 
          className="btn btn-primary add-btn"
          onClick={() => {
            resetForm();
            setIsFormOpen(true);
          }}
        >
          <span className="btn-icon">+</span>
          <span>New Connection</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon total">📊</div>
          <div className="stat-info">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total Connections</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>📁</div>
          <div className="stat-info">
            <span className="stat-value">{stats.input_sor}</span>
            <span className="stat-label">Flat Files</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#6366f1' }}>🗄️</div>
          <div className="stat-info">
            <span className="stat-value">{stats.target_db}</span>
            <span className="stat-label">Destination Databases</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}>🔗</div>
          <div className="stat-info">
            <span className="stat-value">{stats.api_source}</span>
            <span className="stat-label">API Source Feeds</span>
          </div>
        </div>
      </div>

      {/* Connection Table */}
      <div className="connections-table-container">
        <div className="table-header">
          <h2>All Connections</h2>
        </div>
        
        {isLoading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading connections...</p>
          </div>
        ) : connections.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔌</div>
            <h3>No connections yet</h3>
            <p>Create your first connection to get started</p>
            <button 
              className="btn btn-primary"
              onClick={() => {
                resetForm();
                setIsFormOpen(true);
              }}
            >
              + Add Connection
            </button>
          </div>
        ) : (
          <table className="connections-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Configuration</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {connections.map(connection => (
                <tr key={connection.id}>
                  <td>
                    <div className="connection-name-cell">
                      <span 
                        className="type-indicator" 
                        style={{ background: connectionTypes[connection.type]?.color || '#6366f1' }}
                      ></span>
                      <span className="connection-name">{connection.name}</span>
                    </div>
                  </td>
                  <td>
                    <span className="type-badge" style={{ 
                      background: `${connectionTypes[connection.type]?.color}15`,
                      color: connectionTypes[connection.type]?.color 
                    }}>
                      {connectionTypes[connection.type]?.icon} {connectionTypes[connection.type]?.label}
                    </span>
                  </td>
                  <td>
                    <div className="config-preview">
                      {Object.entries(connection.config || {}).slice(0, 2).map(([key, value]) => (
                        <span key={key} className="config-tag">
                          {key}: {key.toLowerCase().includes('password') || key.toLowerCase().includes('auth_value') ? '••••' : String(value).substring(0, 20)}
                        </span>
                      ))}
                      {Object.keys(connection.config || {}).length > 2 && (
                        <span className="config-more">+{Object.keys(connection.config).length - 2} more</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="date-cell">{connection.created_at || 'N/A'}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Form Modal */}
      {isFormOpen && (
        <div className="modal-overlay" onClick={() => setIsFormOpen(false)}>
          <div className="modal-content connection-form" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2>New Connection</h2>
                <p>Add a new data source or target connection</p>
              </div>
              <button 
                className="modal-close-btn"
                onClick={() => {
                  setIsFormOpen(false);
                  resetForm();
                }}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-section">
                <div className="form-group">
                  <label>Connection Name <span className="required">*</span></label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="Enter a unique name for this connection"
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Connection Type <span className="required">*</span></label>
                  <div className="type-selector">
                    {Object.entries(connectionTypes).map(([key, { label, icon, color }]) => (
                      <div
                        key={key}
                        className={`type-option ${formData.type === key ? 'selected' : ''}`}
                        onClick={() => {
                          handleInputChange('type', key);
                          setFormData(prev => ({ ...prev, config: {} }));
                        }}
                        style={{ 
                          borderColor: formData.type === key ? color : 'transparent',
                          background: formData.type === key ? `${color}10` : ''
                        }}
                      >
                        <span className="type-option-icon">{icon}</span>
                        <span className="type-option-label">{label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h3 className="section-title">Configuration</h3>
                <div className="config-grid">
                  {getConfigFields(formData.type).map(field => (
                    <div key={field.key} className={`form-group ${field.type === 'checkbox' ? 'checkbox-group' : ''}`}>
                      <label>{field.label}</label>
                      {renderConfigField(field)}
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-actions">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {
                    setIsFormOpen(false);
                    resetForm();
                  }}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Connection
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConnectionsPage;