"""
Test Planner Service - Data Pipeline Testing Platform
======================================================
This service analyzes the ETL pipeline components and generates a comprehensive
test planning document by understanding:
1. Source data structure and sample data
2. Target database schema and sample data
3. ETL transformation logic
4. Business rules and SCD Type 2 implementation
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Any
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import DatabaseConnection
from utils.llm_svc import call_openai_llm


class TestPlanner:
    """
    Analyzes the ETL pipeline and generates a comprehensive test plan document.
    """

    def __init__(self):
        self.db = DatabaseConnection()
        self.conn = None
        self.cursor = None
        self.analysis_results = {
            'source_data': {},
            'target_schema': {},
            'target_sample_data': [],
            'etl_code': {},
            'transformations': '',
            'business_rules': []
        }

    def connect_db(self):
        """Establish database connection."""
        self.conn = self.db.get_connection()
        self.cursor = self.conn.cursor()
        print("✓ Database connection established.")

    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed.")

    def analyze_source_data(self, csv_file_path: str):
        """
        Analyze the source CSV file to understand schema and sample data.
        
        Args:
            csv_file_path: Path to the source CSV file
        """
        print(f"\n{'='*60}")
        print(f"STEP 1: Analyzing Source Data")
        print(f"{'='*60}")
        print(f"File: {csv_file_path}")

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            rows = list(reader)

        # Store analysis results
        self.analysis_results['source_data'] = {
            'file_path': csv_file_path,
            'columns': headers,
            'column_count': len(headers),
            'row_count': len(rows),
            'sample_rows': rows[:5]  # First 5 rows
        }

        print(f"  ✓ Columns: {', '.join(headers)}")
        print(f"  ✓ Total Columns: {len(headers)}")
        print(f"  ✓ Total Rows: {len(rows)}")
        print(f"  ✓ Sample Data (first 5 rows):")
        for i, row in enumerate(rows[:5], 1):
            print(f"    Row {i}: {row}")

    def analyze_target_schema(self, table_name: str = 'dim_customer'):
        """
        Analyze the target database table schema.
        
        Args:
            table_name: Name of the target table
        """
        print(f"\n{'='*60}")
        print(f"STEP 2: Analyzing Target Database Schema")
        print(f"{'='*60}")
        print(f"Table: {table_name}")

        # Get table schema information for PostgreSQL
        schema_query = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        
        self.cursor.execute(schema_query, (table_name,))
        columns = self.cursor.fetchall()

        schema_info = []
        for col in columns:
            schema_info.append({
                'column_name': col[0],
                'data_type': col[1],
                'is_nullable': col[2],
                'column_default': col[3]
            })

        self.analysis_results['target_schema'] = {
            'table_name': table_name,
            'columns': schema_info,
            'column_count': len(schema_info)
        }

        print(f"  ✓ Table Schema:")
        for col in schema_info:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"    - {col['column_name']}: {col['data_type']} {nullable}{default}")

    def analyze_target_sample_data(self, table_name: str = 'dim_customer', limit: int = 10):
        """
        Fetch sample data from the target table.
        
        Args:
            table_name: Name of the target table
            limit: Number of sample rows to fetch
        """
        print(f"\n{'='*60}")
        print(f"STEP 3: Fetching Target Table Sample Data")
        print(f"{'='*60}")

        query = f"""
        SELECT * FROM {table_name}
        ORDER BY surrogate_key
        LIMIT %s;
        """
        
        self.cursor.execute(query, (limit,))
        rows = self.cursor.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in self.cursor.description]
        
        sample_data = []
        for row in rows:
            sample_data.append(dict(zip(column_names, row)))

        self.analysis_results['target_sample_data'] = sample_data

        print(f"  ✓ Fetched {len(sample_data)} sample rows")
        print(f"  ✓ Columns: {', '.join(column_names)}")

    def analyze_etl_code(self, etl_file_path: str, main_file_path: str):
        """
        Read and analyze the ETL code files.
        
        Args:
            etl_file_path: Path to the ETL script
            main_file_path: Path to the main driver script
        """
        print(f"\n{'='*60}")
        print(f"STEP 4: Analyzing ETL Code")
        print(f"{'='*60}")

        # Read ETL file
        with open(etl_file_path, 'r', encoding='utf-8') as file:
            etl_code = file.read()

        # Read main file
        with open(main_file_path, 'r', encoding='utf-8') as file:
            main_code = file.read()

        self.analysis_results['etl_code'] = {
            'etl_file_path': etl_file_path,
            'main_file_path': main_file_path,
            'etl_code': etl_code,
            'main_code': main_code,
            'etl_lines': len(etl_code.split('\n')),
            'main_lines': len(main_code.split('\n'))
        }

        print(f"  ✓ ETL File: {etl_file_path}")
        print(f"    - Lines of code: {len(etl_code.split('\n'))}")
        print(f"  ✓ Main File: {main_file_path}")
        print(f"    - Lines of code: {len(main_code.split('\n'))}")

    def generate_transformation_summary_with_llm(self):
        """
        Use LLM to generate a comprehensive summary of transformations and business rules.
        """
        print(f"\n{'='*60}")
        print(f"STEP 5: Generating Transformation Summary with LLM")
        print(f"{'='*60}")

        # Prepare context for LLM
        source_columns = ', '.join(self.analysis_results['source_data']['columns'])
        target_columns = ', '.join([col['column_name'] for col in self.analysis_results['target_schema']['columns']])

        prompt = f"""
You are a data engineering expert analyzing an ETL pipeline. Based on the following information, provide a comprehensive summary of the data transformations and business rules.

**SOURCE DATA (CSV):**
- Columns: {source_columns}
- Sample Row: {self.analysis_results['source_data']['sample_rows'][0] if self.analysis_results['source_data']['sample_rows'] else 'N/A'}

**TARGET TABLE (PostgreSQL):**
- Table: {self.analysis_results['target_schema']['table_name']}
- Columns: {target_columns}

**ETL CODE SUMMARY:**
The ETL implements SCD Type 2 (Slowly Changing Dimension Type 2) for customer data.

Key Classes and Methods:
- CustomerSCD2ETL class with methods:
  - create_target_table(): Creates dimension table with surrogate keys, effective dates, and is_current flag
  - extract(): Reads CSV file
  - get_current_record(): Fetches active record for a customer
  - has_scd2_change(): Checks if tracked fields (company_name) changed
  - has_scd1_change(): Checks if Type 1 fields (first_name, last_name, email, phone) changed
  - insert_new_record(): Inserts new customer records
  - expire_record(): Expires old records by setting effective_end_date and is_current=FALSE
  - update_type1_fields(): Updates Type 1 fields in place
  - load(): Main loading logic implementing SCD Type 2
  - run_etl(): Orchestrates the ETL process

**BUSINESS RULES:**
1. SCD Type 2 tracked field: company_name (creates new version when changed)
2. SCD Type 1 fields: first_name, last_name, email, phone (updated in place)
3. Natural key: customer_id
4. Surrogate key: auto-generated sequence
5. Temporal tracking: effective_start_date, effective_end_date, is_current flag

Please provide:
1. **Data Flow Summary**: How data moves from source to target
2. **Key Transformations**: What transformations are applied
3. **Business Rules**: Important business logic and rules
4. **SCD Type 2 Logic**: How historical changes are tracked
5. **Data Quality Considerations**: What should be tested

Keep the response clear, structured, and concise (max 500 words).
"""

        try:
            print("  ⏳ Calling OpenAI LLM to generate summary...")
            summary = call_openai_llm(prompt, model="gpt-4o-mini", max_tokens=1000, temperature=0.3)
            self.analysis_results['transformations'] = summary
            print("  ✓ Transformation summary generated successfully")
            return summary
        except Exception as e:
            print(f"  ✗ Error calling LLM: {e}")
            # Fallback to manual summary
            summary = self._generate_manual_summary()
            self.analysis_results['transformations'] = summary
            return summary

    def _generate_manual_summary(self):
        """Generate a manual summary if LLM is not available."""
        return """
## Data Flow Summary
The ETL pipeline extracts customer data from CSV files, transforms it according to SCD Type 2 logic, and loads it into a PostgreSQL dimension table.

## Key Transformations
1. **Surrogate Key Generation**: Auto-generated SERIAL primary key for each version
2. **Temporal Attributes**: Added effective_start_date, effective_end_date, is_current flag
3. **Audit Columns**: Added created_at and updated_at timestamps
4. **Data Type Mapping**: CSV strings → PostgreSQL VARCHAR/TIMESTAMP/BOOLEAN types

## Business Rules
1. **Natural Key**: customer_id uniquely identifies a customer across versions
2. **SCD Type 2**: company_name changes create new record versions with history
3. **SCD Type 1**: first_name, last_name, email, phone update in place
4. **Current Record**: Only one record per customer_id has is_current=TRUE
5. **Historical Records**: Expired records have is_current=FALSE and effective_end_date set

## SCD Type 2 Logic
- New customers: Insert with is_current=TRUE, effective_end_date=NULL
- Company change: Expire old record (set end date, is_current=FALSE), insert new version
- Other changes: Update existing record in place (SCD Type 1)
- Unchanged: No action taken

## Data Quality Considerations
1. Duplicate prevention: Check existing records before insert
2. Data integrity: Maintain one active record per customer
3. Temporal consistency: Ensure effective dates are sequential
4. Audit trail: All changes tracked with timestamps
"""

    def generate_markdown_report(self, output_file: str = 'etl_analysis_report.md'):
        """
        Generate a comprehensive markdown report of the ETL analysis.
        
        Args:
            output_file: Output file path for the markdown report
        """
        print(f"\n{'='*60}")
        print(f"STEP 6: Generating Markdown Report")
        print(f"{'='*60}")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# ETL Pipeline Analysis Report

**Generated:** {timestamp}  
**Pipeline:** Customer Data SCD Type 2 ETL

---

## 1. Source Data Analysis

### File Information
- **File Path:** `{self.analysis_results['source_data']['file_path']}`
- **Total Columns:** {self.analysis_results['source_data']['column_count']}
- **Total Rows:** {self.analysis_results['source_data']['row_count']}

### Schema
| Column Name | Sample Value |
|-------------|--------------|
"""
        
        # Add source schema
        if self.analysis_results['source_data']['sample_rows']:
            sample_row = self.analysis_results['source_data']['sample_rows'][0]
            for col in self.analysis_results['source_data']['columns']:
                md_content += f"| `{col}` | {sample_row.get(col, 'N/A')} |\n"

        md_content += f"""

### Sample Data (First 3 Rows)
```csv
{','.join(self.analysis_results['source_data']['columns'])}
"""
        for row in self.analysis_results['source_data']['sample_rows'][:3]:
            md_content += ','.join([str(row.get(col, '')) for col in self.analysis_results['source_data']['columns']]) + '\n'
        
        md_content += "```\n\n"

        # Add target schema
        md_content += """---

## 2. Target Database Schema

### Table Information
"""
        md_content += f"- **Table Name:** `{self.analysis_results['target_schema']['table_name']}`\n"
        md_content += f"- **Total Columns:** {self.analysis_results['target_schema']['column_count']}\n\n"

        md_content += """### Table Schema
| Column Name | Data Type | Nullable | Default |
|-------------|-----------|----------|---------|
"""
        for col in self.analysis_results['target_schema']['columns']:
            nullable = "Yes" if col['is_nullable'] == 'YES' else "No"
            default = col['column_default'] if col['column_default'] else "-"
            md_content += f"| `{col['column_name']}` | {col['data_type']} | {nullable} | {default} |\n"

        # Add sample data from target
        md_content += f"""

### Sample Target Data ({len(self.analysis_results['target_sample_data'])} records)
"""
        if self.analysis_results['target_sample_data']:
            md_content += "```\n"
            for i, row in enumerate(self.analysis_results['target_sample_data'][:5], 1):
                md_content += f"\nRecord {i}:\n"
                for key, value in row.items():
                    md_content += f"  {key}: {value}\n"
            md_content += "```\n"

        # Add transformation summary
        md_content += """
---

## 3. ETL Transformation Summary

"""
        md_content += self.analysis_results['transformations']

        md_content += """

---

## 4. ETL Code Analysis

### Files Analyzed
"""
        md_content += f"- **ETL Script:** `{self.analysis_results['etl_code']['etl_file_path']}` ({self.analysis_results['etl_code']['etl_lines']} lines)\n"
        md_content += f"- **Main Driver:** `{self.analysis_results['etl_code']['main_file_path']}` ({self.analysis_results['etl_code']['main_lines']} lines)\n"

        md_content += """

### Key ETL Operations
1. **Extract:** Read CSV file using Python csv.DictReader
2. **Transform:** Apply SCD Type 2 logic based on business rules
3. **Load:** Insert/Update records in PostgreSQL database

### Critical Methods
- `create_target_table()` - Creates dimension table with SCD Type 2 structure
- `get_current_record()` - Retrieves active record for comparison
- `has_scd2_change()` - Detects changes in tracked fields (company_name)
- `has_scd1_change()` - Detects changes in Type 1 fields
- `insert_new_record()` - Inserts new customer versions
- `expire_record()` - Expires old records with effective end date
- `update_type1_fields()` - Updates non-tracked fields in place

---

## 5. Testing Recommendations

### Test Categories

#### 5.1 Data Quality Tests
- Validate all source columns are mapped to target
- Check for NULL values in required fields
- Verify data type compatibility
- Test duplicate customer_id handling

#### 5.2 SCD Type 2 Tests
- **New Customer Insert:** Verify new customers inserted with is_current=TRUE
- **Company Change:** Verify old record expired and new version created
- **Multiple Changes:** Test sequential company changes maintain correct history
- **Unchanged Records:** Verify no unnecessary updates for unchanged data

#### 5.3 SCD Type 1 Tests
- **Name/Email/Phone Updates:** Verify in-place updates without version creation
- **Combined Changes:** Test Type 1 + Type 2 changes in same load

#### 5.4 Temporal Consistency Tests
- Verify only one is_current=TRUE per customer_id
- Check effective_start_date < effective_end_date for expired records
- Validate effective dates align with load dates

#### 5.5 Edge Cases
- Empty CSV file handling
- Malformed CSV data
- Database connection failures
- Concurrent updates to same customer

#### 5.6 Performance Tests
- Large file processing (10K+ records)
- Bulk update scenarios
- Index effectiveness verification

---

## 6. Data Lineage

```
Source CSV (customers_updated.csv)
    ↓
Extract (csv.DictReader)
    ↓
Transform (SCD Type 2 Logic)
    ├─ New Customer → Insert with is_current=TRUE
    ├─ Company Changed → Expire old + Insert new version
    ├─ Type 1 Changed → Update in place
    └─ Unchanged → Skip
    ↓
Load (PostgreSQL dim_customer table)
```

---

## 7. Next Steps

1. **Review this analysis** with stakeholders
2. **Create detailed test cases** based on testing recommendations
3. **Implement automated test scenarios** using the test execution framework
4. **Validate** with sample test data
5. **Execute** comprehensive test suite

---

*End of Report*
"""

        # Write to file
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  ✓ Report generated: {output_path}")
        return output_path

    def run_analysis(self, 
                     csv_file: str = 'input_sor/customers_updated.csv',
                     etl_file: str = 'utils/customer_etl.py',
                     main_file: str = 'main.py',
                     output_file: str = 'etl_analysis_report.md'):
        """
        Execute the complete analysis pipeline.
        
        Args:
            csv_file: Path to source CSV file (relative to python_svc)
            etl_file: Path to ETL script (relative to python_svc)
            main_file: Path to main driver script (relative to python_svc)
            output_file: Output markdown file name
        """
        print("\n" + "="*60)
        print("ETL PIPELINE TEST PLANNER")
        print("="*60)

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            # Step 1: Analyze source data
            csv_path = os.path.join(base_path, csv_file)
            self.analyze_source_data(csv_path)

            # Step 2-3: Connect to DB and analyze target
            self.connect_db()
            self.analyze_target_schema()
            self.analyze_target_sample_data()

            # Step 4: Analyze ETL code
            etl_path = os.path.join(base_path, etl_file)
            main_path = os.path.join(base_path, main_file)
            self.analyze_etl_code(etl_path, main_path)

            # Step 5: Generate transformation summary with LLM
            self.generate_transformation_summary_with_llm()

            # Step 6: Generate markdown report
            report_path = self.generate_markdown_report(output_file)

            print("\n" + "="*60)
            print("✓ ANALYSIS COMPLETE!")
            print("="*60)
            print(f"\nReport saved to: {report_path}")
            print("\nNext Steps:")
            print("  1. Review the generated report")
            print("  2. Use it for test case planning")
            print("  3. Create automated test scenarios")

            return report_path

        except Exception as e:
            print(f"\n✗ Error during analysis: {e}")
            raise
        finally:
            self.close_db()


def main():
    """Main entry point for the test planner service."""
    planner = TestPlanner()
    planner.run_analysis()


if __name__ == "__main__":
    main()
