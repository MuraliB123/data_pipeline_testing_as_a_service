"""
Data Pipeline Testing Platform - Flask API Service
===================================================
This Flask service orchestrates the automated testing pipeline:
1. Test Planner - Analyzes ETL and generates analysis report
2. Scenario Cases - Generates test cases from analysis
3. Execution - Runs test cases and produces results

Endpoints:
- POST /start-signal - Receives start signal from frontend and executes all pipeline steps
- GET /results - Get the latest test results
- GET /connections - Get all connections
- POST /connections - Create a new connection
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Import pipeline components
from agent_svc.test_planner import TestPlanner
from agent_svc.scenario_cases import ScenarioCasesGenerator
from agent_svc.execution import TestExecutionAgent

app = Flask(__name__)
CORS(app)

# Base path for file operations
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Connections storage file
CONNECTIONS_FILE = os.path.join(BASE_PATH,'temp_artifacts', 'connections.json')


def get_timestamp():
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_connections():
    """Load connections from JSON file."""
    if os.path.exists(CONNECTIONS_FILE):
        with open(CONNECTIONS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_connections(connections):
    """Save connections to JSON file."""
    with open(CONNECTIONS_FILE, 'w') as f:
        json.dump(connections, f, indent=2)


@app.route('/start-signal', methods=['POST'])
def start_signal():
    """
    Receives a start signal from the frontend, executes all steps, and responds with a success message.
    Executes: Test Planner -> Scenario Generator -> Test Execution
    """
    try:
        print("\n" + "="*70)
        print("START SIGNAL RECEIVED FROM FRONTEND")
        print("="*70)
        
        # Step 1: Run Test Planner
        print("\n[Step 1/3] Running Test Planner...")
        planner = TestPlanner()
        report_path = planner.run_analysis()
        print(f"  ✓ Analysis report generated: {report_path}")

        # Step 2: Run Scenario Cases Generator
        print("\n[Step 2/3] Running Scenario Cases Generator...")
        generator = ScenarioCasesGenerator()
        test_cases_path = generator.generate_test_cases()
        print(f"  ✓ Test cases generated: {test_cases_path}")

        # Step 3: Run Test Execution
        print("\n[Step 3/3] Running Test Execution Agent...")
        agent = TestExecutionAgent()
        agent.use_llm_planning = False
        results_path = agent.run_all_tests()
        print(f"  ✓ Test execution completed: {results_path}")

        # Load results for summary
        with open(results_path, 'r') as f:
            results = json.load(f)

        print("\n" + "="*70)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)

        return jsonify({
            "status": "success",
            "message": "Pipeline executed successfully from start signal.",
            "report_file": report_path,
            "test_cases_file": test_cases_path,
            "results_file": results_path,
            "summary": {
                "total_tests": results['metadata']['total_tests'],
                "passed": results['metadata']['passed'],
                "failed": results['metadata']['failed'],
                "errors": results['metadata']['errors'],
                "pass_rate": f"{(results['metadata']['passed'] / results['metadata']['total_tests'] * 100):.1f}%" if results['metadata']['total_tests'] > 0 else "0%"
            },
            "timestamp": get_timestamp()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": get_timestamp()
        }), 500


@app.route('/results', methods=['GET'])
def get_results():
    """
    Get the latest test results.
    """
    try:
        results_path = os.path.join(BASE_PATH, 'test_results.json')
        
        if not os.path.exists(results_path):
            return jsonify({
                "status": "error",
                "message": "No test results found. Run the pipeline first."
            }), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        return jsonify({
            "status": "success",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/connections', methods=['GET'])
def get_connections():
    """
    Get all connections.
    """
    try:
        connections = load_connections()
        return jsonify({
            "status": "success",
            "connections": connections
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/connections', methods=['POST'])
def create_connection():
    """
    Create a new connection.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('type'):
            return jsonify({
                "status": "error",
                "message": "Name and type are required"
            }), 400
        
        connections = load_connections()
        
        # Create new connection
        new_connection = {
            "id": str(uuid.uuid4()),
            "name": data['name'],
            "type": data['type'],
            "config": data.get('config', {}),
            "created_at": get_timestamp()
        }
        
        connections.append(new_connection)
        save_connections(connections)
        
        return jsonify({
            "status": "success",
            "connection": new_connection
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Data Pipeline Testing Platform - API Service")
    print("="*60)
    print("\nAvailable Endpoints:")
    print("  POST /start-signal    - Execute complete testing pipeline")
    print("  GET  /results         - Get latest test results")
    print("  GET  /connections     - Get all connections")
    print("  POST /connections     - Create new connection")
    print("\n" + "="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)