"""
Scenario Cases Service - Data Pipeline Testing Platform
========================================================
This service generates test cases based on the ETL analysis report.
Test cases are categorized into:
1. quality_check - SQL queries to validate loaded data quality
2. scenario_check - End-to-end tests with data modifications
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_svc import call_openai_llm


class ScenarioCasesGenerator:
    """
    Generates structured test cases from ETL analysis report.
    """

    def __init__(self, report_path: str = 'etl_analysis_report.md'):
        """
        Initialize the scenario cases generator.
        
        Args:
            report_path: Path to the ETL analysis report markdown file
        """
        self.report_path = report_path
        self.report_content = ""
        self.test_cases = {
            "metadata": {
                "generated_at": "",
                "pipeline_name": "Customer Data SCD Type 2 ETL",
                "source_report": report_path,
                "total_cases": 0,
                "quality_checks": 0,
                "scenario_checks": 0
            },
            "test_cases": []
        }

    def read_report(self):
        """Read the ETL analysis report."""
        print(f"\n{'='*60}")
        print(f"Reading ETL Analysis Report")
        print(f"{'='*60}")
        
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, self.report_path)
        
        with open(full_path, 'r', encoding='utf-8') as file:
            self.report_content = file.read()
        
        print(f"  ✓ Report loaded: {full_path}")
        print(f"  ✓ Content length: {len(self.report_content)} characters")

    def generate_quality_check_cases(self):
        """Generate quality check test cases using LLM."""
        print(f"\n{'='*60}")
        print(f"Generating Quality Check Test Cases")
        print(f"{'='*60}")

        prompt = f"""
Based on the following ETL analysis report, generate data quality test cases as SQL queries.

{self.report_content[:4000]}

Generate 10-12 quality check test cases that validate:
1. Data completeness (all records loaded)
2. Data integrity (primary keys, foreign keys)
3. NULL value checks in required fields
4. SCD Type 2 constraints (only one current record per customer)
5. Temporal consistency (date validations)
6. Data type validations
7. Business rule validations

For EACH test case, provide:
- test_id: Unique identifier (e.g., "QC001", "QC002")
- test_name: Descriptive name
- test_description: What the test validates
- test_type: "quality_check"
- sql_query: The actual SQL query to execute (PostgreSQL syntax)
- expected_result: What the query should return for a passing test
- severity: "critical", "high", "medium", or "low"

Return ONLY a valid JSON array of test case objects. No markdown, no explanation, just the JSON array.
"""

        try:
            print("  ⏳ Calling OpenAI LLM to generate quality checks...")
            response = call_openai_llm(prompt, model="gpt-4o-mini", max_tokens=2500, temperature=0.5)
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            quality_cases = json.loads(response)
            
            print(f"  ✓ Generated {len(quality_cases)} quality check cases")
            return quality_cases
            
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parsing error: {e}")
            print(f"  Response: {response[:200]}...")
            return self._generate_default_quality_checks()
        except Exception as e:
            print(f"  ✗ Error generating quality checks: {e}")
            return self._generate_default_quality_checks()

    def generate_scenario_check_cases(self):
        """Generate scenario check test cases using LLM."""
        print(f"\n{'='*60}")
        print(f"Generating Scenario Check Test Cases")
        print(f"{'='*60}")

        prompt = f"""
Based on the following ETL analysis report, generate end-to-end scenario test cases.

{self.report_content[:4000]}

Generate 8-10 scenario test cases that cover:
1. New customer insertion
2. Company name change (SCD Type 2)
3. Name/email/phone change (SCD Type 1)
4. Combined Type 1 + Type 2 changes
5. Multiple sequential changes to same customer
6. Unchanged records (no updates)
7. New customer + existing customer updates in same file
8. Edge cases (empty values, special characters, etc.)

For EACH test case, provide:
- test_id: Unique identifier (e.g., "SC001", "SC002")
- test_name: Descriptive name
- test_description: What the scenario tests
- test_type: "scenario_check"
- input_data: Array of customer records (JSON objects with customer_id, first_name, last_name, email, company_name, phone)
- expected_outcome: Detailed description of expected results
- validation_queries: Array of SQL queries to validate the outcome
- severity: "critical", "high", "medium", or "low"

Return ONLY a valid JSON array of test case objects. No markdown, no explanation, just the JSON array.
"""

        try:
            print("  ⏳ Calling OpenAI LLM to generate scenario checks...")
            response = call_openai_llm(prompt, model="gpt-4o-mini", max_tokens=3000, temperature=0.5)
            
            # Parse JSON response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            scenario_cases = json.loads(response)
            
            print(f"  ✓ Generated {len(scenario_cases)} scenario check cases")
            return scenario_cases
            
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parsing error: {e}")
            print(f"  ℹ Using default scenario checks instead")
            return self._generate_default_scenario_checks()
        except KeyboardInterrupt:
            print(f"  ⚠ Operation interrupted by user")
            print(f"  ℹ Using default scenario checks instead")
            return self._generate_default_scenario_checks()
        except Exception as e:
            print(f"  ✗ Error generating scenario checks: {e}")
            print(f"  ℹ Using default scenario checks instead")
            return self._generate_default_scenario_checks()

    def _generate_default_quality_checks(self):
        """Generate default quality check test cases as fallback."""
        return [
            {
                "test_id": "QC001",
                "test_name": "Verify Total Record Count",
                "test_description": "Ensure all records from source are loaded into target table",
                "test_type": "quality_check",
                "sql_query": "SELECT COUNT(*) as total_records FROM dim_customer;",
                "expected_result": "Should return count matching source data records",
                "severity": "critical"
            },
            {
                "test_id": "QC002",
                "test_name": "Validate One Current Record Per Customer",
                "test_description": "Ensure only one record has is_current=TRUE for each customer_id",
                "test_type": "quality_check",
                "sql_query": "SELECT customer_id, COUNT(*) as current_count FROM dim_customer WHERE is_current = TRUE GROUP BY customer_id HAVING COUNT(*) > 1;",
                "expected_result": "Should return 0 rows (no duplicates)",
                "severity": "critical"
            },
            {
                "test_id": "QC003",
                "test_name": "Check NULL Values in Required Fields",
                "test_description": "Validate no NULL values in customer_id, effective_start_date, is_current",
                "test_type": "quality_check",
                "sql_query": "SELECT COUNT(*) FROM dim_customer WHERE customer_id IS NULL OR effective_start_date IS NULL OR is_current IS NULL;",
                "expected_result": "Should return 0",
                "severity": "critical"
            },
            {
                "test_id": "QC004",
                "test_name": "Verify Temporal Consistency",
                "test_description": "Check that effective_end_date > effective_start_date for expired records",
                "test_type": "quality_check",
                "sql_query": "SELECT COUNT(*) FROM dim_customer WHERE effective_end_date IS NOT NULL AND effective_end_date <= effective_start_date;",
                "expected_result": "Should return 0",
                "severity": "high"
            },
            {
                "test_id": "QC005",
                "test_name": "Validate Current Records Have NULL End Date",
                "test_description": "Ensure all current records have effective_end_date as NULL",
                "test_type": "quality_check",
                "sql_query": "SELECT COUNT(*) FROM dim_customer WHERE is_current = TRUE AND effective_end_date IS NOT NULL;",
                "expected_result": "Should return 0",
                "severity": "critical"
            }
        ]

    def _generate_default_scenario_checks(self):
        """Generate default scenario check test cases as fallback."""
        return [
            {
                "test_id": "SC001",
                "test_name": "New Customer Insertion",
                "test_description": "Test insertion of a brand new customer record",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C999",
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test.user@email.com",
                        "company_name": "Test Company",
                        "phone": "555-9999"
                    }
                ],
                "expected_outcome": "One new record inserted with is_current=TRUE, effective_end_date=NULL",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C999' AND is_current=TRUE;",
                    "SELECT effective_end_date FROM dim_customer WHERE customer_id='C999' AND is_current=TRUE;"
                ],
                "severity": "critical"
            },
            {
                "test_id": "SC002",
                "test_name": "Company Name Change (SCD Type 2)",
                "test_description": "Test SCD Type 2 behavior when company_name changes",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C001",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@email.com",
                        "company_name": "New Company Inc",
                        "phone": "555-0101"
                    }
                ],
                "expected_outcome": "Old record expired (is_current=FALSE, end_date set), new record created (is_current=TRUE)",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C001';",
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C001' AND is_current=TRUE;",
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C001' AND is_current=FALSE;"
                ],
                "severity": "critical"
            },
            {
                "test_id": "SC003",
                "test_name": "Type 1 Field Updates (Name/Email/Phone)",
                "test_description": "Test SCD Type 1 updates without creating new versions",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C002",
                        "first_name": "Janet",
                        "last_name": "Smith",
                        "email": "janet.smith@newemail.com",
                        "company_name": "MegaData Corp",
                        "phone": "555-0199"
                    }
                ],
                "expected_outcome": "Existing record updated in place, no new version created, same surrogate_key",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C002';",
                    "SELECT first_name, email FROM dim_customer WHERE customer_id='C002' AND is_current=TRUE;"
                ],
                "severity": "high"
            },
            {
                "test_id": "SC004",
                "test_name": "Combined Type 1 and Type 2 Changes",
                "test_description": "Test when both Type 1 fields and company_name change simultaneously",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C003",
                        "first_name": "Mike",
                        "last_name": "Johnson",
                        "email": "mike.j@email.com",
                        "company_name": "NextGen Systems",
                        "phone": "555-0103"
                    }
                ],
                "expected_outcome": "Old record expired, new version created with both company and name changes",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C003';",
                    "SELECT company_name, first_name FROM dim_customer WHERE customer_id='C003' AND is_current=TRUE;"
                ],
                "severity": "critical"
            },
            {
                "test_id": "SC005",
                "test_name": "Unchanged Record Processing",
                "test_description": "Test that unchanged records are not updated unnecessarily",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C005",
                        "first_name": "David",
                        "last_name": "Brown",
                        "email": "david.b@email.com",
                        "company_name": "InnovateTech",
                        "phone": "555-0105"
                    }
                ],
                "expected_outcome": "No changes made, record count and updated_at remain the same",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C005';",
                    "SELECT is_current, effective_end_date FROM dim_customer WHERE customer_id='C005';"
                ],
                "severity": "medium"
            },
            {
                "test_id": "SC006",
                "test_name": "Multiple Customers in Single Load",
                "test_description": "Test processing multiple customers with different change types in one load",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C001",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@email.com",
                        "company_name": "Super Tech Corp",
                        "phone": "555-0101"
                    },
                    {
                        "customer_id": "C888",
                        "first_name": "Alice",
                        "last_name": "Wonder",
                        "email": "alice.w@email.com",
                        "company_name": "Wonder Co",
                        "phone": "555-0888"
                    }
                ],
                "expected_outcome": "C001 gets new version (company change), C888 inserted as new customer",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C001';",
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C888';",
                    "SELECT is_current FROM dim_customer WHERE customer_id IN ('C001', 'C888');"
                ],
                "severity": "high"
            },
            {
                "test_id": "SC007",
                "test_name": "Sequential Company Changes",
                "test_description": "Test multiple company changes for same customer over time",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C004",
                        "first_name": "Emily",
                        "last_name": "Williams",
                        "email": "emily.w@email.com",
                        "company_name": "Ultimate Tech Solutions",
                        "phone": "555-0104"
                    }
                ],
                "expected_outcome": "Multiple versions exist, only latest is current, previous versions have sequential dates",
                "validation_queries": [
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C004';",
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C004' AND is_current=TRUE;",
                    "SELECT COUNT(*) FROM dim_customer WHERE customer_id='C004' AND is_current=FALSE;"
                ],
                "severity": "critical"
            },
            {
                "test_id": "SC008",
                "test_name": "Empty String Handling",
                "test_description": "Test handling of empty or NULL-like values in input data",
                "test_type": "scenario_check",
                "input_data": [
                    {
                        "customer_id": "C777",
                        "first_name": "Test",
                        "last_name": "Empty",
                        "email": "",
                        "company_name": "Empty Test Corp",
                        "phone": ""
                    }
                ],
                "expected_outcome": "Record inserted with empty strings preserved (or handled per business rules)",
                "validation_queries": [
                    "SELECT email, phone FROM dim_customer WHERE customer_id='C777' AND is_current=TRUE;"
                ],
                "severity": "medium"
            }
        ]

    def combine_and_save_test_cases(self, quality_cases: List[Dict], scenario_cases: List[Dict], output_file: str = 'test_cases.json'):
        """
        Combine all test cases and save to JSON file.
        
        Args:
            quality_cases: List of quality check test cases
            scenario_cases: List of scenario check test cases
            output_file: Output JSON file name
        """
        print(f"\n{'='*60}")
        print(f"Combining and Saving Test Cases")
        print(f"{'='*60}")

        # Update metadata
        self.test_cases['metadata']['generated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_cases['metadata']['quality_checks'] = len(quality_cases)
        self.test_cases['metadata']['scenario_checks'] = len(scenario_cases)
        self.test_cases['metadata']['total_cases'] = len(quality_cases) + len(scenario_cases)

        # Combine test cases
        self.test_cases['test_cases'] = quality_cases + scenario_cases

        # Save to file
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_path, output_file)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_cases, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Test cases saved to: {output_path}")
        print(f"  ✓ Total test cases: {self.test_cases['metadata']['total_cases']}")
        print(f"    - Quality checks: {self.test_cases['metadata']['quality_checks']}")
        print(f"    - Scenario checks: {self.test_cases['metadata']['scenario_checks']}")

        return output_path

    def generate_test_cases(self, output_file: str = 'test_cases.json'):
        """
        Execute the complete test case generation pipeline.
        
        Args:
            output_file: Output JSON file name
        """
        print("\n" + "="*60)
        print("SCENARIO CASES GENERATOR")
        print("="*60)

        try:
            # Step 1: Read analysis report
            self.read_report()

            # Step 2: Generate quality check cases
            quality_cases = self.generate_quality_check_cases()

            # Step 3: Generate scenario check cases
            scenario_cases = self.generate_scenario_check_cases()

            # Step 4: Combine and save
            output_path = self.combine_and_save_test_cases(quality_cases, scenario_cases, output_file)

            print("\n" + "="*60)
            print("✓ TEST CASE GENERATION COMPLETE!")
            print("="*60)
            print(f"\nTest cases file: {output_path}")
            print("\nNext Steps:")
            print("  1. Review the generated test cases")
            print("  2. Modify or add custom test cases if needed")
            print("  3. Use execution service to run the tests")

            return output_path

        except Exception as e:
            print(f"\n✗ Error during test case generation: {e}")
            raise


def main():
    """Main entry point for the scenario cases generator."""
    generator = ScenarioCasesGenerator()
    generator.generate_test_cases()


if __name__ == "__main__":
    main()
