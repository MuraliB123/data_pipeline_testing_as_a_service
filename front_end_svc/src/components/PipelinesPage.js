import React, { useState, useEffect } from 'react';

const PipelinesPage = ({ onBack }) => {
  // State management
  const [pipelines, setPipelines] = useState([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('connections');
  const [connections, setConnections] = useState([]);
  
  // Form data state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    // Connections tab
    sourceConnections: [],
    targetConnections: [],
    // Context tab
    contextType: 'github',
    githubRepo: '',
    githubBranch: 'main',
    folderPath: '',
    fileName: '',
    etlDescription: '',
    // Execution Engine tab
    webhookUrl: '',
    jobServer: '',
    jobName: '',
    triggerType: 'manual',
    schedule: '',
    authType: 'none',
    authToken: '',
    // Test Cases tab
    testCases: [],
    testCaseText: ''
  });

  // Mock pipelines data
  const mockPipelines = [
    {
      id: 'pipe-001',
      name: 'Customer ETL Pipeline',
      description: 'Daily customer data synchronization from CSV to PostgreSQL',
      status: 'active',
      sourceConnections: ['Customer Initial Data', 'Customer Updated Data'],
      targetConnections: ['Destination PostgreSQL DB'],
      lastRun: '2026-01-31 14:30:00',
      testsCount: 24,
      passRate: 92
    },
    {
      id: 'pipe-002',
      name: 'Sales Analytics Pipeline',
      description: 'Weekly sales data aggregation and reporting',
      status: 'active',
      sourceConnections: ['Sales API Feed'],
      targetConnections: ['Analytics DWH'],
      lastRun: '2026-01-30 08:00:00',
      testsCount: 18,
      passRate: 100
    },
    {
      id: 'pipe-003',
      name: 'Inventory Sync Pipeline',
      description: 'Real-time inventory synchronization across warehouses',
      status: 'paused',
      sourceConnections: ['Warehouse API'],
      targetConnections: ['Inventory DB'],
      lastRun: '2026-01-28 16:45:00',
      testsCount: 31,
      passRate: 87
    }
  ];

  // Tab configuration
  const tabs = [
    { id: 'connections', label: 'Connections', icon: '🔗', description: 'Select source and target connections' },
    { id: 'context', label: 'Context', icon: '📁', description: 'Provide ETL script source code details' },
    { id: 'execution', label: 'Execution Engine', icon: '⚡', description: 'Configure job trigger settings' },
    { id: 'testcases', label: 'Test Cases', icon: '🧪', description: 'Define declarative test cases' }
  ];

  // Fetch initial data
  useEffect(() => {
    fetchPipelines();
    fetchConnections();
  }, []);

  const fetchPipelines = async () => {
    setIsLoading(true);
    // Simulating API call - replace with actual backend call later
    setTimeout(() => {
      setPipelines(mockPipelines);
      setIsLoading(false);
    }, 500);
  };

  const fetchConnections = async () => {
    try {
      const response = await fetch('http://localhost:5000/connections');
      if (response.ok) {
        const data = await response.json();
        setConnections(data.connections || []);
      }
    } catch (error) {
      console.error('Error fetching connections:', error);
      // Mock connections for development
      setConnections([
        { id: 'conn-001', name: 'Customer Initial Data', type: 'input_sor' },
        { id: 'conn-002', name: 'Customer Updated Data', type: 'input_sor' },
        { id: 'conn-003', name: 'Destination PostgreSQL DB', type: 'target_db' },
        { id: 'conn-004', name: 'External API Feed', type: 'api_source' }
      ]);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      sourceConnections: [],
      targetConnections: [],
      contextType: 'github',
      githubRepo: '',
      githubBranch: 'main',
      folderPath: '',
      fileName: '',
      etlDescription: '',
      webhookUrl: '',
      jobServer: '',
      jobName: '',
      triggerType: 'manual',
      schedule: '',
      authType: 'none',
      authToken: '',
      testCases: [],
      testCaseText: ''
    });
    setActiveTab('connections');
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleConnectionToggle = (connectionId, connectionType) => {
    const field = connectionType === 'source' ? 'sourceConnections' : 'targetConnections';
    setFormData(prev => {
      const current = prev[field];
      if (current.includes(connectionId)) {
        return { ...prev, [field]: current.filter(id => id !== connectionId) };
      } else {
        return { ...prev, [field]: [...current, connectionId] };
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // TODO: Implement backend API call
    console.log('Pipeline Data:', formData);
    // Add to local state for now
    const newPipeline = {
      id: `pipe-${Date.now()}`,
      name: formData.name,
      description: formData.description,
      status: 'draft',
      sourceConnections: formData.sourceConnections.map(id => 
        connections.find(c => c.id === id)?.name || id
      ),
      targetConnections: formData.targetConnections.map(id => 
        connections.find(c => c.id === id)?.name || id
      ),
      lastRun: 'Never',
      testsCount: formData.testCases.length || 0,
      passRate: 0
    };
    setPipelines(prev => [newPipeline, ...prev]);
    setIsFormOpen(false);
    resetForm();
  };

  const parseTestCases = (text) => {
    // Simple parser for YAML/Gherkin-like test cases
    const cases = [];
    const lines = text.split('\n');
    let currentCase = null;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('Feature:') || trimmed.startsWith('Scenario:') || trimmed.startsWith('- name:')) {
        if (currentCase) cases.push(currentCase);
        currentCase = { name: trimmed.replace(/^(Feature:|Scenario:|- name:)\s*/, ''), steps: [] };
      } else if (trimmed.startsWith('Given') || trimmed.startsWith('When') || trimmed.startsWith('Then') || trimmed.startsWith('And') || trimmed.startsWith('-')) {
        if (currentCase) currentCase.steps.push(trimmed);
      }
    });
    if (currentCase) cases.push(currentCase);
    return cases;
  };

  const handleTestCaseUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        handleInputChange('testCaseText', text);
        const parsed = parseTestCases(text);
        handleInputChange('testCases', parsed);
      };
      reader.readAsText(file);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active': return 'status-active';
      case 'paused': return 'status-paused';
      case 'draft': return 'status-draft';
      case 'error': return 'status-error';
      default: return '';
    }
  };

  const connectionTypes = {
    input_sor: { label: 'Flat Files', icon: '📁', color: '#10b981' },
    target_db: { label: 'Database', icon: '🗄️', color: '#6366f1' },
    api_source: { label: 'API', icon: '🔗', color: '#f59e0b' }
  };

  // Render Connections Tab
  const renderConnectionsTab = () => (
    <div className="tab-content-inner">
      <div className="connection-selection-section">
        <div className="selection-group">
          <h4 className="selection-title">
            <span className="selection-icon">📥</span>
            Source Connections
          </h4>
          <p className="selection-desc">Select one or more data sources for this pipeline</p>
          <div className="connection-grid">
            {connections
              .filter(c => c.type === 'input_sor' || c.type === 'api_source')
              .map(conn => (
                <div
                  key={conn.id}
                  className={`connection-card selectable ${formData.sourceConnections.includes(conn.id) ? 'selected' : ''}`}
                  onClick={() => handleConnectionToggle(conn.id, 'source')}
                  title={conn.name}
                >
                  <div className="connection-card-header">
                    <span 
                      className="connection-type-icon"
                      style={{ background: connectionTypes[conn.type]?.color }}
                    >
                      {connectionTypes[conn.type]?.icon}
                    </span>
                    <span className={`selection-check ${formData.sourceConnections.includes(conn.id) ? 'checked' : ''}`}>
                      {formData.sourceConnections.includes(conn.id) ? '✓' : ''}
                    </span>
                  </div>
                  <h5 className="connection-card-name">{conn.name}</h5>
                  <span className="connection-card-type">{connectionTypes[conn.type]?.label}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="selection-divider">
          <span className="divider-icon">→</span>
        </div>

        <div className="selection-group">
          <h4 className="selection-title">
            <span className="selection-icon">📤</span>
            Target Connections
          </h4>
          <p className="selection-desc">Select the destination for processed data</p>
          <div className="connection-grid">
            {connections
              .filter(c => c.type === 'target_db')
              .map(conn => (
                <div
                  key={conn.id}
                  className={`connection-card selectable ${formData.targetConnections.includes(conn.id) ? 'selected' : ''}`}
                  onClick={() => handleConnectionToggle(conn.id, 'target')}
                  title={conn.name}
                >
                  <div className="connection-card-header">
                    <span 
                      className="connection-type-icon"
                      style={{ background: connectionTypes[conn.type]?.color }}
                    >
                      {connectionTypes[conn.type]?.icon}
                    </span>
                    <span className={`selection-check ${formData.targetConnections.includes(conn.id) ? 'checked' : ''}`}>
                      {formData.targetConnections.includes(conn.id) ? '✓' : ''}
                    </span>
                  </div>
                  <h5 className="connection-card-name">{conn.name}</h5>
                  <span className="connection-card-type">{connectionTypes[conn.type]?.label}</span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Render Context Tab
  const renderContextTab = () => (
    <div className="tab-content-inner">
      <div className="context-section">
        <div className="context-type-selector">
          <h4 className="section-subtitle">Source Code Location</h4>
          <div className="context-type-options">
            <div
              className={`context-type-card ${formData.contextType === 'github' ? 'selected' : ''}`}
              onClick={() => handleInputChange('contextType', 'github')}
            >
              <span className="context-type-icon">🐙</span>
              <span className="context-type-label">GitHub Repository</span>
            </div>
            <div
              className={`context-type-card ${formData.contextType === 'local' ? 'selected' : ''}`}
              onClick={() => handleInputChange('contextType', 'local')}
            >
              <span className="context-type-icon">💻</span>
              <span className="context-type-label">Local Path</span>
            </div>
            <div
              className={`context-type-card ${formData.contextType === 'upload' ? 'selected' : ''}`}
              onClick={() => handleInputChange('contextType', 'upload')}
            >
              <span className="context-type-icon">📤</span>
              <span className="context-type-label">Upload File</span>
            </div>
          </div>
        </div>

        {formData.contextType === 'github' && (
          <div className="context-form">
            <div className="form-row">
              <div className="form-group">
                <label>GitHub Repository URL <span className="required">*</span></label>
                <input
                  type="text"
                  value={formData.githubRepo}
                  onChange={(e) => handleInputChange('githubRepo', e.target.value)}
                  placeholder="https://github.com/org/repo"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Branch</label>
                <input
                  type="text"
                  value={formData.githubBranch}
                  onChange={(e) => handleInputChange('githubBranch', e.target.value)}
                  placeholder="main"
                  className="form-input"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Folder Path</label>
                <input
                  type="text"
                  value={formData.folderPath}
                  onChange={(e) => handleInputChange('folderPath', e.target.value)}
                  placeholder="src/etl/pipelines"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>ETL Script File Name <span className="required">*</span></label>
                <input
                  type="text"
                  value={formData.fileName}
                  onChange={(e) => handleInputChange('fileName', e.target.value)}
                  placeholder="customer_etl.py"
                  className="form-input"
                />
              </div>
            </div>
          </div>
        )}

        {formData.contextType === 'local' && (
          <div className="context-form">
            <div className="form-row">
              <div className="form-group full-width">
                <label>Local File Path <span className="required">*</span></label>
                <input
                  type="text"
                  value={formData.folderPath}
                  onChange={(e) => handleInputChange('folderPath', e.target.value)}
                  placeholder="C:\projects\etl\scripts\customer_etl.py"
                  className="form-input"
                />
              </div>
            </div>
          </div>
        )}

        {formData.contextType === 'upload' && (
          <div className="context-form">
            <div className="upload-zone">
              <input
                type="file"
                id="etl-file-upload"
                accept=".py,.sql,.js"
                className="file-input-hidden"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) handleInputChange('fileName', file.name);
                }}
              />
              <label htmlFor="etl-file-upload" className="upload-zone-label">
                <span className="upload-icon">📄</span>
                <span className="upload-text">
                  {formData.fileName || 'Click or drag to upload ETL script'}
                </span>
                <span className="upload-hint">Supports .py, .sql, .js files</span>
              </label>
            </div>
          </div>
        )}

        <div className="form-group full-width">
          <label>ETL Description (Optional)</label>
          <textarea
            value={formData.etlDescription}
            onChange={(e) => handleInputChange('etlDescription', e.target.value)}
            placeholder="Describe what this ETL pipeline does, its data transformations, business rules, etc."
            className="form-textarea"
            rows={4}
          />
        </div>
      </div>
    </div>
  );

  // Render Execution Engine Tab
  const renderExecutionTab = () => (
    <div className="tab-content-inner">
      <div className="execution-section">
        <div className="section-intro">
          <span className="section-intro-icon">⚡</span>
          <div>
            <h4>Job Execution Configuration</h4>
            <p>Configure how and when the pipeline tests should be triggered</p>
          </div>
        </div>

        <div className="execution-form">
          <div className="form-group">
            <label>Job Server <span className="required">*</span></label>
            <input
              type="text"
              value={formData.jobServer}
              onChange={(e) => handleInputChange('jobServer', e.target.value)}
              placeholder="jenkins.company.com or airflow.company.com"
              className="form-input"
            />
            <span className="form-hint">Enter the hostname or IP of your job orchestration server</span>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Job Name <span className="required">*</span></label>
              <input
                type="text"
                value={formData.jobName}
                onChange={(e) => handleInputChange('jobName', e.target.value)}
                placeholder="customer-etl-pipeline"
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Trigger Type</label>
              <select
                value={formData.triggerType}
                onChange={(e) => handleInputChange('triggerType', e.target.value)}
                className="form-select"
              >
                <option value="manual">Manual</option>
                <option value="webhook">Webhook</option>
                <option value="scheduled">Scheduled</option>
                <option value="on-commit">On Commit</option>
              </select>
            </div>
          </div>

          {formData.triggerType === 'webhook' && (
            <div className="form-group">
              <label>Webhook URL <span className="required">*</span></label>
              <input
                type="text"
                value={formData.webhookUrl}
                onChange={(e) => handleInputChange('webhookUrl', e.target.value)}
                placeholder="https://jenkins.company.com/job/customer-etl/build"
                className="form-input"
              />
            </div>
          )}

          {formData.triggerType === 'scheduled' && (
            <div className="form-group">
              <label>Schedule (Cron Expression)</label>
              <input
                type="text"
                value={formData.schedule}
                onChange={(e) => handleInputChange('schedule', e.target.value)}
                placeholder="0 0 * * * (every day at midnight)"
                className="form-input"
              />
              <span className="form-hint">Standard cron format: minute hour day month weekday</span>
            </div>
          )}

          <div className="form-section-divider">
            <span>Authentication</span>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Auth Type</label>
              <select
                value={formData.authType}
                onChange={(e) => handleInputChange('authType', e.target.value)}
                className="form-select"
              >
                <option value="none">None</option>
                <option value="bearer">Bearer Token</option>
                <option value="api_key">API Key</option>
                <option value="basic">Basic Auth</option>
              </select>
            </div>
            {formData.authType !== 'none' && (
              <div className="form-group">
                <label>Auth Token/Key <span className="required">*</span></label>
                <input
                  type="password"
                  value={formData.authToken}
                  onChange={(e) => handleInputChange('authToken', e.target.value)}
                  placeholder="Enter authentication token"
                  className="form-input"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Render Test Cases Tab
  const renderTestCasesTab = () => (
    <div className="tab-content-inner">
      <div className="testcases-section">
        <div className="section-intro">
          <span className="section-intro-icon">🧪</span>
          <div>
            <h4>Declarative Test Cases</h4>
            <p>Upload or write YAML/Gherkin-like test cases for your pipeline</p>
          </div>
        </div>

        <div className="testcase-upload-area">
          <input
            type="file"
            id="testcase-upload"
            accept=".yaml,.yml,.feature,.txt"
            className="file-input-hidden"
            onChange={handleTestCaseUpload}
          />
          <label htmlFor="testcase-upload" className="upload-drop-zone">
            <span className="upload-icon-large">📋</span>
            <span className="upload-title">Upload Test Cases File</span>
            <span className="upload-subtitle">Supports .yaml, .yml, .feature files</span>
          </label>
        </div>

        <div className="testcase-divider">
          <span>or write test cases manually</span>
        </div>

        <div className="testcase-editor">
          <div className="editor-header">
            <span className="editor-label">Test Cases (YAML/Gherkin format)</span>
            <button 
              type="button"
              className="btn-text"
              onClick={() => {
                const sample = `Feature: Customer Data Validation
  Scenario: Validate customer email format
    Given the source data contains customer records
    When the ETL pipeline processes the data
    Then all email addresses should be valid format

  Scenario: Check for duplicate records
    Given customer data from multiple sources
    When data is merged into target
    Then no duplicate customer_id should exist

- name: Row Count Validation
  source: customers_initial.csv
  target: customers_table
  assertion: source_count == target_count

- name: Data Completeness Check
  target: customers_table
  assertion: null_count(email) == 0`;
                handleInputChange('testCaseText', sample);
                handleInputChange('testCases', parseTestCases(sample));
              }}
            >
              Load Sample
            </button>
          </div>
          <textarea
            value={formData.testCaseText}
            onChange={(e) => {
              handleInputChange('testCaseText', e.target.value);
              handleInputChange('testCases', parseTestCases(e.target.value));
            }}
            placeholder={`Feature: Data Validation
  Scenario: Validate row counts
    Given the source file has records
    When ETL pipeline completes
    Then target table should have same count

- name: Column Validation
  assertion: schema matches expected`}
            className="form-textarea testcase-textarea"
            rows={12}
          />
        </div>

        {formData.testCases.length > 0 && (
          <div className="parsed-testcases">
            <h4 className="parsed-title">Parsed Test Cases ({formData.testCases.length})</h4>
            <div className="testcase-list">
              {formData.testCases.map((tc, index) => (
                <div key={index} className="testcase-item">
                  <span className="testcase-number">{index + 1}</span>
                  <div className="testcase-content">
                    <span className="testcase-name">{tc.name}</span>
                    <span className="testcase-steps">{tc.steps.length} steps</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Render tab content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'connections': return renderConnectionsTab();
      case 'context': return renderContextTab();
      case 'execution': return renderExecutionTab();
      case 'testcases': return renderTestCasesTab();
      default: return null;
    }
  };

  const currentTabIndex = tabs.findIndex(t => t.id === activeTab);
  const isFirstTab = currentTabIndex === 0;
  const isLastTab = currentTabIndex === tabs.length - 1;

  // Render the pipeline creation form inline
  const renderCreatePipelineForm = () => (
    <div className="pipeline-create-inline">
      {/* Create Form Header */}
      <div className="create-form-header">
        <div className="create-form-title">
          <span className="create-icon">🚀</span>
          <div>
            <h2>Create New Pipeline</h2>
            <p>Configure your data pipeline for automated testing</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="pipeline-inline-form">
        {/* Pipeline Basic Info */}
        <div className="pipeline-basic-info-inline">
          <div className="form-row">
            <div className="form-group">
              <label>Pipeline Name <span className="required">*</span></label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Customer ETL Pipeline"
                className="form-input"
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Brief description of the pipeline"
                className="form-input"
              />
            </div>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="pipeline-tabs-inline">
          {tabs.map((tab, index) => (
            <button
              key={tab.id}
              type="button"
              className={`pipeline-tab ${activeTab === tab.id ? 'active' : ''} ${index < currentTabIndex ? 'completed' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-step">{index + 1}</span>
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="tab-content-inline">
          {renderTabContent()}
        </div>

        {/* Form Actions */}
        <div className="form-actions-inline">
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={() => {
              setIsFormOpen(false);
              resetForm();
            }}
          >
            ← Back to Pipelines
          </button>
          <div className="nav-buttons">
            {!isFirstTab && (
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => setActiveTab(tabs[currentTabIndex - 1].id)}
              >
                ← Previous
              </button>
            )}
            {!isLastTab ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setActiveTab(tabs[currentTabIndex + 1].id)}
              >
                Next →
              </button>
            ) : (
              <button type="submit" className="btn btn-primary btn-create">
                🚀 Create Pipeline
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );

  // Render the pipelines list view
  const renderPipelinesList = () => (
    <>
      {/* Stats Overview */}
      <div className="pipeline-stats-row">
        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(99, 102, 241, 0.1)' }}>
            <span className="stat-icon" style={{ color: '#6366f1' }}>⚡</span>
          </div>
          <div className="stat-info">
            <span className="stat-value">{pipelines.length}</span>
            <span className="stat-label">Total Pipelines</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
            <span className="stat-icon" style={{ color: '#10b981' }}>✓</span>
          </div>
          <div className="stat-info">
            <span className="stat-value">{pipelines.filter(p => p.status === 'active').length}</span>
            <span className="stat-label">Active</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(245, 158, 11, 0.1)' }}>
            <span className="stat-icon" style={{ color: '#f59e0b' }}>⏸️</span>
          </div>
          <div className="stat-info">
            <span className="stat-value">{pipelines.filter(p => p.status === 'paused').length}</span>
            <span className="stat-label">Paused</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(99, 102, 241, 0.1)' }}>
            <span className="stat-icon" style={{ color: '#6366f1' }}>📈</span>
          </div>
          <div className="stat-info">
            <span className="stat-value">
              {pipelines.length > 0 ? Math.round(pipelines.reduce((acc, p) => acc + p.passRate, 0) / pipelines.length) : 0}%
            </span>
            <span className="stat-label">Avg Pass Rate</span>
          </div>
        </div>
      </div>

      {/* Pipelines Table */}
      <div className="pipelines-table-container">
        <div className="table-header">
          <h2>All Pipelines</h2>
          <div className="table-actions">
            <input 
              type="text" 
              placeholder="Search pipelines..." 
              className="search-input"
            />
            <select className="filter-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </div>

        {isLoading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading pipelines...</p>
          </div>
        ) : pipelines.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔄</div>
            <h3>No pipelines yet</h3>
            <p>Create your first pipeline to start testing</p>
            <button 
              className="btn btn-primary"
              onClick={() => {
                resetForm();
                setIsFormOpen(true);
              }}
            >
              + Create Pipeline
            </button>
          </div>
        ) : (
          <div className="pipeline-cards-grid">
            {pipelines.map(pipeline => (
              <div key={pipeline.id} className="pipeline-card">
                <div className="pipeline-card-header">
                  <div className="pipeline-info">
                    <h3 className="pipeline-name">{pipeline.name}</h3>
                    <span className={`pipeline-status-badge ${getStatusBadgeClass(pipeline.status)}`}>
                      {pipeline.status}
                    </span>
                  </div>
                  <button className="pipeline-menu-btn">⋮</button>
                </div>
                <p className="pipeline-description">{pipeline.description}</p>
                
                <div className="pipeline-connections">
                  <div className="connection-flow">
                    <div className="flow-sources">
                      {pipeline.sourceConnections.map((conn, i) => (
                        <span key={i} className="flow-tag source">{conn}</span>
                      ))}
                    </div>
                    <span className="flow-arrow">→</span>
                    <div className="flow-targets">
                      {pipeline.targetConnections.map((conn, i) => (
                        <span key={i} className="flow-tag target">{conn}</span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pipeline-metrics">
                  <div className="metric">
                    <span className="metric-value">{pipeline.testsCount}</span>
                    <span className="metric-label">Tests</span>
                  </div>
                  <div className="metric">
                    <span className="metric-value">{pipeline.passRate}%</span>
                    <span className="metric-label">Pass Rate</span>
                  </div>
                  <div className="metric">
                    <span className="metric-value-small">{pipeline.lastRun}</span>
                    <span className="metric-label">Last Run</span>
                  </div>
                </div>

                <div className="pipeline-card-actions">
                  <button className="btn-action-secondary">View Details</button>
                  <button className="btn-action-primary">Run Tests</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );

  return (
    <div className="pipelines-page">
      {/* Header */}
      <div className="pipelines-header">
        <div className="header-left">
          <button className="back-btn" onClick={isFormOpen ? () => { setIsFormOpen(false); resetForm(); } : onBack}>
            <span>←</span>
            <span>{isFormOpen ? 'Back to Pipelines' : 'Back to Dashboard'}</span>
          </button>
          <div className="header-title">
            <h1>{isFormOpen ? 'New Pipeline' : 'Pipelines'}</h1>
            <p>{isFormOpen ? 'Configure your data pipeline for automated testing' : 'Configure and manage your data pipeline test suites'}</p>
          </div>
        </div>
        {!isFormOpen && (
          <button 
            className="btn btn-primary add-btn"
            onClick={() => {
              resetForm();
              setIsFormOpen(true);
            }}
          >
            <span className="btn-icon">+</span>
            <span>New Pipeline</span>
          </button>
        )}
      </div>

      {/* Content: Either list or create form */}
      {isFormOpen ? renderCreatePipelineForm() : renderPipelinesList()}
    </div>
  );
};

export default PipelinesPage;
