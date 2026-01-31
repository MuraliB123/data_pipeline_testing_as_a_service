"""
ETL Script for Customer Data with SCD Type 2 Implementation
============================================================
This module handles the Extract, Transform, Load process for customer data
implementing Slowly Changing Dimension Type 2 (SCD2) to track historical changes
in the company_name field.

SCD Type 2 tracks changes by:
- Creating new records when tracked attributes change
- Maintaining effective_start_date and effective_end_date
- Using is_current flag to identify the active record
"""

import csv
import psycopg2
from datetime import datetime
from typing import List, Dict, Optional
from utils.db_connection import DatabaseConnection


class CustomerSCD2ETL:
    """
    ETL class implementing SCD Type 2 for customer dimension table.
    Tracks changes in company_name field while maintaining full history.
    """

    def __init__(self):
        self.db = DatabaseConnection()
        self.conn = None
        self.cursor = None
        # Fields that trigger a new version when changed (SCD Type 2)
        self.tracked_fields = ['company_name']
        # Fields that update in place (SCD Type 1)
        self.type1_fields = ['first_name', 'last_name', 'email', 'phone']

    def connect(self):
        """Establish database connection."""
        self.conn = self.db.get_connection()
        self.cursor = self.conn.cursor()
        print("Database connection established.")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_target_table(self):
        """
        Create the customer dimension table with SCD Type 2 structure.
        Drops existing table if present (for demo purposes).
        """
        drop_table_query = """
        DROP TABLE IF EXISTS dim_customer;
        """
        
        create_table_query = """
        CREATE TABLE dim_customer (
            surrogate_key SERIAL PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            company_name VARCHAR(255),
            phone VARCHAR(50),
            effective_start_date TIMESTAMP NOT NULL,
            effective_end_date TIMESTAMP NULL,
            is_current BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX idx_customer_id ON dim_customer(customer_id);
        CREATE INDEX idx_is_current ON dim_customer(is_current);
        """
        
        self.cursor.execute(drop_table_query)
        self.cursor.execute(create_table_query)
        self.conn.commit()
        print("Target table 'dim_customer' created successfully.")

    def extract(self, file_path: str) -> List[Dict]:
        """
        Extract customer data from CSV file.
        
        Args:
            file_path: Path to the source CSV file
            
        Returns:
            List of dictionaries containing customer records
        """
        records = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                records.append(dict(row))
        
        print(f"Extracted {len(records)} records from {file_path}")
        return records

    def get_current_record(self, customer_id: str) -> Optional[Dict]:
        """
        Retrieve the current active record for a customer.
        
        Args:
            customer_id: The business key for the customer
            
        Returns:
            Dictionary with current record or None if not found
        """
        query = """
        SELECT surrogate_key, customer_id, first_name, last_name, 
               email, company_name, phone, effective_start_date
        FROM dim_customer
        WHERE customer_id = %s AND is_current = TRUE
        """
        self.cursor.execute(query, (customer_id,))
        row = self.cursor.fetchone()
        
        if row:
            return {
                'surrogate_key': row[0],
                'customer_id': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'email': row[4],
                'company_name': row[5],
                'phone': row[6],
                'effective_start_date': row[7]
            }
        return None

    def has_scd2_change(self, source_record: Dict, target_record: Dict) -> bool:
        """
        Check if any SCD Type 2 tracked field has changed.
        
        Args:
            source_record: New record from source
            target_record: Existing record from target
            
        Returns:
            True if any tracked field changed, False otherwise
        """
        for field in self.tracked_fields:
            if source_record.get(field) != target_record.get(field):
                return True
        return False

    def has_scd1_change(self, source_record: Dict, target_record: Dict) -> bool:
        """
        Check if any SCD Type 1 field has changed.
        
        Args:
            source_record: New record from source
            target_record: Existing record from target
            
        Returns:
            True if any Type 1 field changed, False otherwise
        """
        for field in self.type1_fields:
            if source_record.get(field) != target_record.get(field):
                return True
        return False

    def insert_new_record(self, record: Dict, effective_date: datetime):
        """
        Insert a new customer record.
        
        Args:
            record: Customer record to insert
            effective_date: Start date for the record
        """
        insert_query = """
        INSERT INTO dim_customer 
            (customer_id, first_name, last_name, email, company_name, phone,
             effective_start_date, effective_end_date, is_current)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, TRUE)
        """
        self.cursor.execute(insert_query, (
            record['customer_id'],
            record['first_name'],
            record['last_name'],
            record['email'],
            record['company_name'],
            record['phone'],
            effective_date
        ))

    def expire_record(self, surrogate_key: int, effective_date: datetime):
        """
        Expire an existing record by setting end date and is_current flag.
        
        Args:
            surrogate_key: Primary key of record to expire
            effective_date: End date for the record
        """
        update_query = """
        UPDATE dim_customer
        SET effective_end_date = %s,
            is_current = FALSE,
            updated_at = CURRENT_TIMESTAMP
        WHERE surrogate_key = %s
        """
        self.cursor.execute(update_query, (effective_date, surrogate_key))

    def update_type1_fields(self, surrogate_key: int, record: Dict):
        """
        Update SCD Type 1 fields in place.
        
        Args:
            surrogate_key: Primary key of record to update
            record: Source record with new values
        """
        update_query = """
        UPDATE dim_customer
        SET first_name = %s,
            last_name = %s,
            email = %s,
            phone = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE surrogate_key = %s
        """
        self.cursor.execute(update_query, (
            record['first_name'],
            record['last_name'],
            record['email'],
            record['phone'],
            surrogate_key
        ))

    def load(self, records: List[Dict], load_date: datetime = None):
        """
        Load records into target table implementing SCD Type 2 logic.
        
        Args:
            records: List of source records to process
            load_date: Date to use for effective dates (defaults to now)
        """
        if load_date is None:
            load_date = datetime.now()

        stats = {
            'inserted': 0,
            'updated_scd2': 0,
            'updated_scd1': 0,
            'unchanged': 0
        }

        for record in records:
            existing = self.get_current_record(record['customer_id'])

            if existing is None:
                # New customer - insert
                self.insert_new_record(record, load_date)
                stats['inserted'] += 1
                print(f"  INSERT: New customer {record['customer_id']}")

            elif self.has_scd2_change(record, existing):
                # SCD Type 2 change detected - expire old and insert new
                self.expire_record(existing['surrogate_key'], load_date)
                self.insert_new_record(record, load_date)
                stats['updated_scd2'] += 1
                print(f"  SCD2 UPDATE: Customer {record['customer_id']} - "
                      f"company changed from '{existing['company_name']}' to '{record['company_name']}'")

            elif self.has_scd1_change(record, existing):
                # SCD Type 1 change - update in place
                self.update_type1_fields(existing['surrogate_key'], record)
                stats['updated_scd1'] += 1
                print(f"  SCD1 UPDATE: Customer {record['customer_id']} - attributes updated")

            else:
                stats['unchanged'] += 1

        self.conn.commit()
        
        print(f"\nLoad Summary:")
        print(f"  - New records inserted: {stats['inserted']}")
        print(f"  - SCD2 updates (new versions): {stats['updated_scd2']}")
        print(f"  - SCD1 updates (in-place): {stats['updated_scd1']}")
        print(f"  - Unchanged records: {stats['unchanged']}")

        return stats

    def run_etl(self, source_file: str, load_date: datetime = None):
        """
        Execute the complete ETL pipeline.
        
        Args:
            source_file: Path to source CSV file
            load_date: Optional date for effective dates
        """
        print(f"\n{'='*60}")
        print(f"Starting ETL Process: {source_file}")
        print(f"{'='*60}\n")

        # Extract
        records = self.extract(source_file)

        # Transform (minimal transformation for this example)
        # In real scenarios, you might add data cleansing, validation, etc.

        # Load with SCD Type 2
        stats = self.load(records, load_date)

        print(f"\n{'='*60}")
        print("ETL Process Completed")
        print(f"{'='*60}\n")

        return stats

    def display_current_state(self):
        """Display all records in the dimension table for verification."""
        query = """
        SELECT surrogate_key, customer_id, first_name, last_name, 
               company_name, effective_start_date, effective_end_date, is_current
        FROM dim_customer
        ORDER BY customer_id, effective_start_date
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        print(f"\n{'='*100}")
        print("Current State of dim_customer Table")
        print(f"{'='*100}")
        print(f"{'SK':<5} {'Cust ID':<10} {'Name':<20} {'Company':<25} {'Start Date':<20} {'End Date':<20} {'Current'}")
        print(f"{'-'*100}")
        
        for row in rows:
            end_date = str(row[6])[:19] if row[6] else 'NULL'
            start_date = str(row[5])[:19] if row[5] else 'NULL'
            print(f"{row[0]:<5} {row[1]:<10} {row[2]+' '+row[3]:<20} {row[4]:<25} {start_date:<20} {end_date:<20} {row[7]}")
