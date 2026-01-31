# 🔬 DataTest Pro - Data Pipeline Testing as a Service

An automated testing platform for ETL/Data Pipelines that leverages AI to analyze, generate test cases, and validate data transformations with comprehensive insights.

![Dashboard](Screenshot%202026-01-31%20161440.png)

## 📋 Overview

DataTest Pro is a full-stack application designed to automate the testing of data pipelines, specifically focusing on:

- **ETL Pipeline Analysis** - Automatically analyzes source data, target schemas, and transformation logic
- **AI-Powered Test Generation** - Uses OpenAI GPT models to generate comprehensive test cases
- **Automated Test Execution** - Runs quality checks and scenario validations automatically
- **Real-time Results Dashboard** - React-based UI for monitoring and viewing test results

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Landing Page │  │  Dashboard   │  │   Results Modal      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP REST API
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Flask API)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Test Planner │→ │Scenario Cases│→ │  Test Execution      │   │
│  │   Agent      │  │  Generator   │  │     Agent            │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  PostgreSQL  │  │  OpenAI API  │  │   CSV Data Files     │   │
│  │   Database   │  │  (GPT-4o)    │  │   (Source Data)      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📸 Screenshots

### Application Interface
![Test Results Interface](WhatsApp%20Image%202026-01-31%20at%203.54.00%20PM.jpeg)

### Pipeline Execution
![Pipeline Execution](WhatsApp%20Image%202026-01-31%20at%203.54.18%20PM.jpeg)

## ✨ Features

### 🔍 Test Planner Agent
- Analyzes source CSV data structure and sample data
- Inspects target database schema (PostgreSQL)
- Reviews ETL transformation code
- Generates comprehensive analysis report in Markdown

### 🧪 Scenario Cases Generator
- **Quality Checks** - SQL queries to validate data integrity, completeness, and business rules
- **Scenario Checks** - End-to-end tests with data modifications (SCD Type 2 validations)
- AI-powered test case generation using OpenAI GPT models

### ⚡ Test Execution Agent
- Automated test execution with database backup/restore
- Supports both quality checks and scenario-based testing
- Detailed results with pass/fail status and execution metrics

### 🎨 React Dashboard
- Modern, responsive UI
- Real-time progress tracking
- Detailed test results visualization
- Pipeline selection and management

## 🛠️ Tech Stack

### Backend
- **Python 3.12** - Core programming language
- **Flask** - REST API framework
- **Flask-CORS** - Cross-origin resource sharing
- **PostgreSQL** - Target database (psycopg2)
- **OpenAI API** - AI-powered test generation
- **SQLAlchemy** - Database ORM

### Frontend
- **React 18** - UI framework
- **CSS3** - Styling (custom components)

## 📁 Project Structure

```
data_pipeline_testing_as_a_service/
├── front_end_svc/                 # React Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── components/
│   │       ├── Dashboard.js       # Main dashboard component
│   │       ├── LandingPage.js     # Landing page
│   │       ├── ProgressModal.js   # Test execution progress
│   │       └── ResultsModal.js    # Test results display
│   └── package.json
│
├── python_svc/                    # Python Backend
│   ├── main.py                    # Flask API entry point
│   ├── requirements.txt           # Python dependencies
│   ├── test_cases.json           # Generated test cases
│   ├── test_results.json         # Test execution results
│   ├── etl_analysis_report.md    # ETL analysis output
│   │
│   ├── agent_svc/                # AI Agents
│   │   ├── test_planner.py       # ETL analysis agent
│   │   ├── scenario_cases.py     # Test case generator
│   │   ├── execution.py          # Test execution agent
│   │   └── validation.py         # Validation utilities
│   │
│   ├── utils/                    # Utilities
│   │   ├── db_connection.py      # Database connection
│   │   ├── llm_svc.py           # OpenAI LLM service
│   │   └── customer_etl.py      # ETL implementation
│   │
│   └── input_sor/               # Source data
│       ├── customers_initial.csv
│       └── customers_updated.csv
│
└── readme.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd python_svc
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv env
   # Windows
   .\env\Scripts\activate
   # Linux/Mac
   source env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install flask flask-cors psycopg2-binary openai python-dotenv sqlalchemy
   ```

4. Configure environment variables:
   ```bash
   # Create .env file with:
   OPENAI_API_KEY=your_openai_api_key
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

5. Start the Flask server:
   ```bash
   python main.py
   ```
   Server runs on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd front_end_svc
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   Application runs on `http://localhost:3000`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/start-signal` | Triggers the full testing pipeline |
| GET | `/results` | Retrieves the latest test results |

### Example Response

```json
{
  "status": "success",
  "message": "Pipeline executed successfully",
  "summary": {
    "total_tests": 20,
    "passed": 18,
    "failed": 2,
    "errors": 0,
    "pass_rate": "90.0%"
  },
  "timestamp": "2026-01-31 16:14:40"
}
```
---

Built with ❤️ for Data Engineers
