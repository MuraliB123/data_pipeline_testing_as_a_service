# ETL Pipeline Analysis Report

**Generated:** 2026-01-31 16:14:03  
**Pipeline:** Customer Data SCD Type 2 ETL

---

## 1. Source Data Analysis

### File Information
- **File Path:** `C:\Users\MuraliB\Pictures\data_pipeline_testing_as_a_service\python_svc\input_sor/customers_updated.csv`
- **Total Columns:** 6
- **Total Rows:** 7

### Schema
| Column Name | Sample Value |
|-------------|--------------|
| `customer_id` | C001 |
| `first_name` | John |
| `last_name` | Doe |
| `email` | john.doe@email.com |
| `company_name` | NeoTech Industries |
| `phone` | 555-0101 |


### Sample Data (First 3 Rows)
```csv
customer_id,first_name,last_name,email,company_name,phone
C001,John,Doe,john.doe@email.com,NeoTech Industries,555-0101
C002,Jane,Smith,jane.smith@email.com,MegaData Corp,555-0102
C003,Michael,Johnson,michael.j@email.com,CloudBase Systems,555-0103
```

---

## 2. Target Database Schema

### Table Information
- **Table Name:** `dim_customer`
- **Total Columns:** 12

### Table Schema
| Column Name | Data Type | Nullable | Default |
|-------------|-----------|----------|---------|
| `surrogate_key` | integer | No | nextval('dim_customer_surrogate_key_seq'::regclass) |
| `customer_id` | character varying | No | - |
| `first_name` | character varying | Yes | - |
| `last_name` | character varying | Yes | - |
| `email` | character varying | Yes | - |
| `company_name` | character varying | Yes | - |
| `phone` | character varying | Yes | - |
| `effective_start_date` | timestamp without time zone | No | - |
| `effective_end_date` | timestamp without time zone | Yes | - |
| `is_current` | boolean | No | true |
| `created_at` | timestamp without time zone | Yes | CURRENT_TIMESTAMP |
| `updated_at` | timestamp without time zone | Yes | CURRENT_TIMESTAMP |


### Sample Target Data (10 records)
```

Record 1:
  surrogate_key: 1
  customer_id: C001
  first_name: John
  last_name: Doe
  email: john.doe@email.com
  company_name: TechCorp Inc
  phone: 555-0101
  effective_start_date: 2026-01-01 00:00:00
  effective_end_date: 2026-01-31 14:03:33.723916
  is_current: False
  created_at: 2026-01-31 08:27:06.220286
  updated_at: 2026-01-31 08:34:07.469842

Record 2:
  surrogate_key: 2
  customer_id: C002
  first_name: Jane
  last_name: Smith
  email: jane.smith@email.com
  company_name: DataSoft LLC
  phone: 555-0102
  effective_start_date: 2026-01-01 00:00:00
  effective_end_date: 2026-01-31 00:00:00
  is_current: False
  created_at: 2026-01-31 08:27:06.220286
  updated_at: 2026-01-31 08:27:09.364461

Record 3:
  surrogate_key: 3
  customer_id: C003
  first_name: Michael
  last_name: Johnson
  email: michael.j@email.com
  company_name: CloudBase Systems
  phone: 555-0103
  effective_start_date: 2026-01-01 00:00:00
  effective_end_date: None
  is_current: True
  created_at: 2026-01-31 08:27:06.220286
  updated_at: 2026-01-31 08:27:06.220286

Record 4:
  surrogate_key: 4
  customer_id: C004
  first_name: Emily
  last_name: Williams
  email: emily.w@email.com
  company_name: TechCorp Inc
  phone: 555-0104
  effective_start_date: 2026-01-01 00:00:00
  effective_end_date: 2026-01-31 00:00:00
  is_current: False
  created_at: 2026-01-31 08:27:06.220286
  updated_at: 2026-01-31 08:27:09.364461

Record 5:
  surrogate_key: 5
  customer_id: C005
  first_name: David
  last_name: Brown
  email: david.b@email.com
  company_name: InnovateTech
  phone: 555-0105
  effective_start_date: 2026-01-01 00:00:00
  effective_end_date: None
  is_current: True
  created_at: 2026-01-31 08:27:06.220286
  updated_at: 2026-01-31 08:27:06.220286
```

---

## 3. ETL Transformation Summary

### Data Flow Summary
The ETL process begins with the extraction of customer data from a CSV file. The `extract()` method reads the source data, which includes fields such as `customer_id`, `first_name`, `last_name`, `email`, `company_name`, and `phone`. The data is then transformed and loaded into the target PostgreSQL table `dim_customer`. The `run_etl()` method orchestrates this process, ensuring that data is correctly processed and stored.

### Key Transformations
1. **Surrogate Key Generation**: Each record in the target table receives an auto-generated surrogate key, which serves as a unique identifier independent of the natural key (`customer_id`).
2. **Effective Date Tracking**: The transformation includes setting `effective_start_date` to the current timestamp when a new record is created. If a record is updated, the `effective_end_date` of the previous record is set to the current timestamp, and `is_current` is updated to `FALSE`.
3. **Field Updates**: 
   - **Type 1 Fields**: The fields `first_name`, `last_name`, `email`, and `phone` are updated in place without creating a new record.
   - **Type 2 Field**: The `company_name` field is tracked for changes. If it changes, a new record is created with the updated `company_name`, while the previous record is expired.

### Business Rules
1. **SCD Type 2 Tracking**: The `company_name` field is the only field tracked for historical changes. When it changes, a new version of the customer record is created.
2. **SCD Type 1 Updates**: The fields `first_name`, `last_name`, `email`, and `phone` are updated directly in the existing record, reflecting the latest information without maintaining history.
3. **Natural Key**: The `customer_id` serves as the natural key for identifying unique customers.
4. **Surrogate Key**: An auto-generated sequence is used to create a surrogate key for each record in the `dim_customer` table.
5. **Temporal Tracking**: The ETL process maintains temporal data through `effective_start_date`, `effective_end_date`, and the `is_current` flag to indicate the active record.

### SCD Type 2 Logic
The SCD Type 2 logic is implemented through the following steps:
- The `get_current_record()` method retrieves the active record for a given `customer_id`.
- The `has_scd2_change()` method checks if the `company_name` has changed compared to the current record.
- If a change is detected, the `expire_record()` method is invoked to set the `effective_end_date` of the current record and mark it as not current (`is_current=FALSE`).
- A new record is then inserted with the updated `company_name`, along with the current timestamp as the `effective_start_date` and `is_current=TRUE`.

### Data Quality Considerations
1. **Data Completeness**: Ensure that all required fields in the CSV are populated before processing.
2. **Data Consistency**: Validate that `customer_id` is unique in the source data to prevent duplicate entries.
3. **Change Detection Accuracy**: Test the logic for detecting changes in `company_name` and ensure Type 1 fields are updated correctly.
4. **Temporal Integrity**: Verify that effective dates are correctly assigned and that no overlapping records exist for the same `customer_id`.
5. **Error Handling**: Implement checks for file read errors, database connection issues, and data type mismatches during the ETL process.

---

## 4. ETL Code Analysis

### Files Analyzed
- **ETL Script:** `C:\Users\MuraliB\Pictures\data_pipeline_testing_as_a_service\python_svc\utils/customer_etl.py` (333 lines)
- **Main Driver:** `C:\Users\MuraliB\Pictures\data_pipeline_testing_as_a_service\python_svc\main.py` (136 lines)


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
