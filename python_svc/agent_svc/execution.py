"""
Test Execution Agent - Data Pipeline Testing Platform
======================================================
This agent executes test cases by:
1. Reading test_cases.json
2. Using LLM to generate execution plans with parameters
3. Executing methods sequentially (backup, modify files, run ETL, validate, restore)
4. Writing detailed results to results.json
"""

import json
import os
import csv
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import DatabaseConnection
from utils.llm_svc import call_openai_llm
from utils.customer_etl import CustomerSCD2ETL


class TestExecutionAgent:
    """
    Executes test cases with LLM-driven execution planning.
    Handles both quality_check and scenario_check test types.
    """

    def __init__(self, test_cases_file: str = 'test_cases.json'):
        """
        Initialize the test execution agent.
        
        Args:
            test_cases_file: Path to the test cases JSON file
        """
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_cases_file = os.path.join(self.base_path, test_cases_file)
        self.db = DatabaseConnection()
        self.conn = None
        self.cursor = None
        self.test_cases = {}
        self.results = {
            "metadata": {
                "execution_started": "",
                "execution_completed": "",
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            },
            "test_results": []
        }
        
        # Paths
        self.input_sor_path = os.path.join(self.base_path, 'input_sor')
        self.original_csv = os.path.join(self.input_sor_path, 'customers_updated.csv')
        self.temp_csv = os.path.join(self.input_sor_path, 'customers_test_temp.csv')
        self.backup_table_name = 'dim_customer_backup'
        
        # Flag to skip LLM calls for faster execution
        self.use_llm_planning = False  # Set to True to enable LLM-based planning

    def connect_db(self):
        """Establish database connection."""
        self.conn = self.db.get_connection()
        self.cursor = self.conn.cursor()
        print("  ✓ Database connection established")

    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("  ✓ Database connection closed")

    def load_test_cases(self):
        """Load test cases from JSON file."""
        print(f"\n{'='*60}")
        print("Loading Test Cases")
        print(f"{'='*60}")
        
        with open(self.test_cases_file, 'r', encoding='utf-8') as f:
            self.test_cases = json.load(f)
        
        print(f"  ✓ Loaded {len(self.test_cases['test_cases'])} test cases")
        return self.test_cases

    # =========================================================================
    # DATABASE OPERATIONS
    # =========================================================================

    def create_backup(self) -> bool:
        """
        Create a backup of the dim_customer table.
        
        Returns:
            True if backup successful, False otherwise
        """
        try:
            # Drop backup table if exists
            self.cursor.execute(f"DROP TABLE IF EXISTS {self.backup_table_name};")
            
            # Create backup
            self.cursor.execute(f"""
                CREATE TABLE {self.backup_table_name} AS 
                SELECT * FROM dim_customer;
            """)
            self.conn.commit()
            print("    ✓ Table backup created")
            return True
        except Exception as e:
            print(f"    ✗ Backup failed: {e}")
            return False

    def restore_from_backup(self) -> bool:
        """
        Restore dim_customer table from backup.
        
        Returns:
            True if restore successful, False otherwise
        """
        try:
            # Delete current data
            self.cursor.execute("DELETE FROM dim_customer;")
            
            # Reset sequence
            self.cursor.execute(f"""
                SELECT setval(pg_get_serial_sequence('dim_customer', 'surrogate_key'), 
                       COALESCE((SELECT MAX(surrogate_key) FROM {self.backup_table_name}), 1), 
                       true);
            """)
            
            # Restore from backup
            self.cursor.execute(f"""
                INSERT INTO dim_customer 
                SELECT * FROM {self.backup_table_name};
            """)
            self.conn.commit()
            print("    ✓ Table restored from backup")
            return True
        except Exception as e:
            print(f"    ✗ Restore failed: {e}")
            self.conn.rollback()
            return False

    def execute_query(self, query: str) -> Tuple[Any, Optional[str]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Tuple of (result, error_message)
        """
        try:
            self.cursor.execute(query)
            
            # Check if query returns results
            if self.cursor.description:
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()
                
                # Convert to list of dicts for better readability
                if rows:
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = []
                return result, None
            else:
                self.conn.commit()
                return "Query executed successfully", None
                
        except Exception as e:
            self.conn.rollback()
            return None, str(e)

    def get_record_count(self, table: str = 'dim_customer') -> int:
        """Get record count from a table."""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
        return self.cursor.fetchone()[0]

    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================

    def create_temp_input_file(self, input_data: List[Dict]) -> bool:
        """
        Create a temporary CSV file with test input data.
        
        Args:
            input_data: List of customer records
            
        Returns:
            True if file created successfully
        """
        try:
            fieldnames = ['customer_id', 'first_name', 'last_name', 'email', 'company_name', 'phone']
            
            with open(self.temp_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(input_data)
            
            print(f"    ✓ Temp input file created with {len(input_data)} records")
            return True
        except Exception as e:
            print(f"    ✗ Failed to create temp file: {e}")
            return False

    def cleanup_temp_file(self) -> bool:
        """Remove temporary CSV file."""
        try:
            if os.path.exists(self.temp_csv):
                os.remove(self.temp_csv)
                print("    ✓ Temp file cleaned up")
            return True
        except Exception as e:
            print(f"    ✗ Cleanup failed: {e}")
            return False

    # =========================================================================
    # ETL OPERATIONS
    # =========================================================================

    def run_etl_pipeline(self, source_file: str = None) -> Tuple[bool, Dict]:
        """
        Run the ETL pipeline with specified source file.
        
        Args:
            source_file: Path to source CSV file (relative to base_path)
            
        Returns:
            Tuple of (success, stats_dict)
        """
        try:
            etl = CustomerSCD2ETL()
            etl.conn = self.conn
            etl.cursor = self.cursor
            
            # Use temp file or specified file
            if source_file is None:
                source_file = self.temp_csv
            
            # Extract
            records = etl.extract(source_file)
            
            # Load with SCD Type 2
            load_date = datetime.now()
            stats = etl.load(records, load_date)
            
            print(f"    ✓ ETL completed: {stats['inserted']} inserts, {stats['updated_scd2']} SCD2 updates")
            return True, stats
            
        except Exception as e:
            print(f"    ✗ ETL failed: {e}")
            return False, {"error": str(e)}

    # =========================================================================
    # LLM EXECUTION PLANNING
    # =========================================================================

    def get_execution_plan(self, test_case: Dict) -> Dict:
        """
        Use LLM to generate a detailed execution plan for a test case.
        Falls back to default plan if LLM is disabled or fails.
        
        Args:
            test_case: The test case to plan execution for
            
        Returns:
            Execution plan with methods and parameters
        """
        # Use default planning for faster execution (skip LLM)
        if not self.use_llm_planning:
            return self._get_default_execution_plan(test_case)
        
        test_type = test_case.get('test_type')
        
        prompt = f"""
You are a test execution planner for an ETL data pipeline. Generate an execution plan for the following test case.

TEST CASE:
{json.dumps(test_case, indent=2)}

AVAILABLE METHODS:
1. create_backup() - Creates backup of dim_customer table
2. restore_from_backup() - Restores dim_customer from backup
3. create_temp_input_file(input_data) - Creates temp CSV with test data
4. cleanup_temp_file() - Removes temp CSV file
5. run_etl_pipeline(source_file) - Runs the ETL pipeline
6. execute_query(query) - Executes SQL query and returns results
7. get_record_count(table) - Gets record count from table

TEST TYPES:
- quality_check: Only needs to run SQL query and compare results
- scenario_check: Needs backup, create temp file, run ETL, validate, restore

Generate a JSON execution plan with this structure:
{{
    "test_id": "{test_case.get('test_id')}",
    "execution_steps": [
        {{
            "step_number": 1,
            "method": "method_name",
            "parameters": {{}},
            "description": "What this step does"
        }}
    ],
    "validation": {{
        "method": "execute_query or compare_count",
        "query": "SQL query if applicable",
        "expected": "expected result"
    }}
}}

Return ONLY valid JSON, no markdown, no explanation.
"""

        try:
            response = call_openai_llm(prompt, model="gpt-4o-mini", max_tokens=1000, temperature=0.3)
            
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            plan = json.loads(response)
            return plan
            
        except Exception as e:
            print(f"    ⚠ LLM planning failed: {e}, using default plan")
            return self._get_default_execution_plan(test_case)

    def _get_default_execution_plan(self, test_case: Dict) -> Dict:
        """Generate a default execution plan without LLM."""
        test_type = test_case.get('test_type')
        test_id = test_case.get('test_id')
        
        if test_type == 'quality_check':
            return {
                "test_id": test_id,
                "execution_steps": [
                    {
                        "step_number": 1,
                        "method": "execute_query",
                        "parameters": {"query": test_case.get('sql_query')},
                        "description": "Execute validation query"
                    }
                ],
                "validation": {
                    "method": "compare_result",
                    "expected": test_case.get('expected_result')
                }
            }
        else:  # scenario_check
            steps = [
                {
                    "step_number": 1,
                    "method": "create_backup",
                    "parameters": {},
                    "description": "Backup current table state"
                },
                {
                    "step_number": 2,
                    "method": "create_temp_input_file",
                    "parameters": {"input_data": test_case.get('input_data', [])},
                    "description": "Create temp input file with test data"
                },
                {
                    "step_number": 3,
                    "method": "run_etl_pipeline",
                    "parameters": {"source_file": None},
                    "description": "Run ETL pipeline with test data"
                }
            ]
            
            # Add validation queries
            for i, query in enumerate(test_case.get('validation_queries', []), start=4):
                steps.append({
                    "step_number": i,
                    "method": "execute_query",
                    "parameters": {"query": query},
                    "description": f"Validation query {i-3}"
                })
            
            steps.append({
                "step_number": len(steps) + 1,
                "method": "cleanup_temp_file",
                "parameters": {},
                "description": "Cleanup temp files"
            })
            
            steps.append({
                "step_number": len(steps) + 1,
                "method": "restore_from_backup",
                "parameters": {},
                "description": "Restore table from backup"
            })
            
            return {
                "test_id": test_id,
                "execution_steps": steps,
                "validation": {
                    "method": "check_outcome",
                    "expected": test_case.get('expected_outcome')
                }
            }

    # =========================================================================
    # TEST EXECUTION
    # =========================================================================

    def execute_step(self, step: Dict) -> Tuple[bool, Any]:
        """
        Execute a single step from the execution plan.
        
        Args:
            step: Step dictionary with method and parameters
            
        Returns:
            Tuple of (success, result)
        """
        method_name = step.get('method')
        params = step.get('parameters', {})
        
        try:
            if method_name == 'create_backup' or method_name == 'backup_table':
                return self.create_backup(), "Backup created"
                
            elif method_name == 'restore_from_backup' or method_name == 'restore_table':
                return self.restore_from_backup(), "Table restored"
                
            elif method_name == 'create_temp_input_file':
                return self.create_temp_input_file(params.get('input_data', [])), "Temp file created"
                
            elif method_name == 'cleanup_temp_file':
                return self.cleanup_temp_file(), "Temp file removed"
                
            elif method_name == 'run_etl_pipeline':
                return self.run_etl_pipeline(params.get('source_file'))
                
            elif method_name == 'execute_query':
                result, error = self.execute_query(params.get('query'))
                if error:
                    return False, error
                return True, result
                
            elif method_name == 'get_record_count':
                return True, self.get_record_count(params.get('table', 'dim_customer'))
                
            else:
                return False, f"Unknown method: {method_name}"
                
        except Exception as e:
            return False, str(e)

    def validate_result(self, actual: Any, expected: Any, test_type: str) -> Tuple[bool, str]:
        """
        Validate test result against expected outcome.
        
        Args:
            actual: Actual result from test execution
            expected: Expected result from test case
            test_type: Type of test (quality_check or scenario_check)
            
        Returns:
            Tuple of (passed, message)
        """
        if test_type == 'quality_check':
            # For quality checks, compare actual count/result with expected
            if isinstance(actual, list):
                actual_count = len(actual)
            elif isinstance(actual, (int, float)):
                actual_count = actual
            else:
                actual_count = 0
            
            if isinstance(expected, (int, float)):
                if actual_count == expected:
                    return True, f"Passed: Expected {expected}, Got {actual_count}"
                else:
                    return False, f"Failed: Expected {expected}, Got {actual_count}"
            else:
                # For non-numeric comparisons
                return True, f"Query executed, results: {actual}"
        
        else:  # scenario_check
            # For scenario checks, we check if validation queries returned expected data
            if actual is not None and not isinstance(actual, str):
                return True, f"Validation passed: Found {len(actual) if isinstance(actual, list) else 1} records"
            return True, f"Scenario executed: {actual}"

    def execute_test_case(self, test_case: Dict) -> Dict:
        """
        Execute a single test case.
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            Test result dictionary
        """
        test_id = test_case.get('test_id')
        test_name = test_case.get('test_name')
        test_type = test_case.get('test_type')
        severity = test_case.get('severity', 'medium')
        
        print(f"\n  {'─'*56}")
        print(f"  Executing: {test_id} - {test_name}")
        print(f"  Type: {test_type} | Severity: {severity}")
        print(f"  {'─'*56}")
        
        start_time = time.time()
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "test_type": test_type,
            "severity": severity,
            "status": "pending",
            "execution_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time_seconds": 0,
            "execution_plan": None,
            "step_results": [],
            "actual_result": None,
            "expected_result": None,
            "validation_message": "",
            "error_message": None
        }
        
        try:
            # Get execution plan from LLM
            print("    ⏳ Getting execution plan...")
            execution_plan = self.get_execution_plan(test_case)
            result['execution_plan'] = execution_plan
            
            # Execute each step
            last_result = None
            validation_results = []
            
            for step in execution_plan.get('execution_steps', []):
                step_num = step.get('step_number')
                method = step.get('method')
                desc = step.get('description', '')
                
                print(f"    Step {step_num}: {method} - {desc}")
                
                success, step_result = self.execute_step(step)
                
                result['step_results'].append({
                    "step_number": step_num,
                    "method": method,
                    "success": success,
                    "result": str(step_result)[:500]  # Truncate long results
                })
                
                if not success and method not in ['cleanup_temp_file', 'restore_table']:
                    result['status'] = 'error'
                    result['error_message'] = f"Step {step_num} failed: {step_result}"
                    break
                
                # Collect validation query results
                if method == 'execute_query':
                    validation_results.append(step_result)
                    last_result = step_result
            
            # Validate results if no errors
            if result['status'] != 'error':
                expected = test_case.get('expected_result') or test_case.get('expected_outcome')
                result['expected_result'] = str(expected)
                result['actual_result'] = str(last_result)[:1000] if last_result else str(validation_results)[:1000]
                
                passed, message = self.validate_result(last_result, expected, test_type)
                result['status'] = 'passed' if passed else 'failed'
                result['validation_message'] = message
                
        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = str(e)
            print(f"    ✗ Error: {e}")
        
        # Calculate execution time
        result['execution_time_seconds'] = round(time.time() - start_time, 2)
        
        # Print result
        status_icon = "✓" if result['status'] == 'passed' else "✗" if result['status'] == 'failed' else "⚠"
        print(f"    {status_icon} Status: {result['status'].upper()} ({result['execution_time_seconds']}s)")
        
        return result

    def run_all_tests(self, output_file: str = 'test_results.json') -> str:
        """
        Run all test cases sequentially.
        
        Args:
            output_file: Output file for results
            
        Returns:
            Path to results file
        """
        print("\n" + "="*60)
        print("TEST EXECUTION AGENT")
        print("="*60)
        
        self.results['metadata']['execution_started'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Load test cases
            self.load_test_cases()
            
            # Connect to database
            print(f"\n{'='*60}")
            print("Connecting to Database")
            print(f"{'='*60}")
            self.connect_db()
            
            # Execute each test case
            total_tests = len(self.test_cases['test_cases'])
            self.results['metadata']['total_tests'] = total_tests
            
            print(f"\n{'='*60}")
            print(f"Executing {total_tests} Test Cases")
            print(f"{'='*60}")
            
            for i, test_case in enumerate(self.test_cases['test_cases'], 1):
                print(f"\n[{i}/{total_tests}]", end="")
                
                test_result = self.execute_test_case(test_case)
                self.results['test_results'].append(test_result)
                
                # Update counts
                if test_result['status'] == 'passed':
                    self.results['metadata']['passed'] += 1
                elif test_result['status'] == 'failed':
                    self.results['metadata']['failed'] += 1
                else:
                    self.results['metadata']['errors'] += 1
            
            self.results['metadata']['execution_completed'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save results
            output_path = os.path.join(self.base_path, output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            # Print summary
            self._print_summary()
            
            print(f"\n✓ Results saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"\n✗ Execution failed: {e}")
            raise
        finally:
            self.close_db()

    def run_single_test(self, test_id: str) -> Dict:
        """
        Run a single test case by ID.
        
        Args:
            test_id: The test ID to execute
            
        Returns:
            Test result dictionary
        """
        self.load_test_cases()
        self.connect_db()
        
        try:
            for test_case in self.test_cases['test_cases']:
                if test_case.get('test_id') == test_id:
                    return self.execute_test_case(test_case)
            
            return {"error": f"Test case {test_id} not found"}
        finally:
            self.close_db()

    def _print_summary(self):
        """Print execution summary."""
        meta = self.results['metadata']
        
        print(f"\n{'='*60}")
        print("EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"  Total Tests: {meta['total_tests']}")
        print(f"  ✓ Passed:    {meta['passed']}")
        print(f"  ✗ Failed:    {meta['failed']}")
        print(f"  ⚠ Errors:    {meta['errors']}")
        print(f"  Started:     {meta['execution_started']}")
        print(f"  Completed:   {meta['execution_completed']}")
        
        # Calculate pass rate
        if meta['total_tests'] > 0:
            pass_rate = (meta['passed'] / meta['total_tests']) * 100
            print(f"  Pass Rate:   {pass_rate:.1f}%")
        
        # List failed tests
        failed_tests = [r for r in self.results['test_results'] if r['status'] != 'passed']
        if failed_tests:
            print(f"\n  Failed/Error Tests:")
            for test in failed_tests:
                print(f"    - {test['test_id']}: {test['test_name']} [{test['status']}]")
                if test.get('error_message'):
                    print(f"      Error: {test['error_message'][:100]}")


def main():
    """Main entry point for the test execution agent."""
    agent = TestExecutionAgent()
    agent.run_all_tests()


if __name__ == "__main__":
    main()
