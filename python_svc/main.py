"""
Data Pipeline Testing Platform - Main Driver
=============================================
This script runs the incremental ETL process for customer data updates.
Processes customers_updated.csv with SCD Type 2 implementation.
"""

from datetime import datetime
from utils.customer_etl import CustomerSCD2ETL


def main():
    """
    Main driver function to execute the incremental ETL pipeline.
    Processes only the updated customer data file.
    """
    etl = CustomerSCD2ETL()

    try:
        # Establish connection
        etl.connect()

        # Display state before processing
        print("\n" + "=" * 60)
        print("Current State BEFORE Processing")
        print("=" * 60)
        etl.display_current_state()

        # Incremental Load - Process updated customer data
        print("\n" + "=" * 60)
        print("Processing Incremental Load: customers_updated.csv")
        print("=" * 60)
        
        # Use current timestamp for the load
        load_date = datetime.now()
        etl.run_etl("input_sor/customers_updated.csv", load_date)

        # Display final state after processing
        print("\n" + "=" * 60)
        print("Current State AFTER Processing")
        print("=" * 60)
        etl.display_current_state()

        print("\n" + "=" * 60)
        print("ETL Pipeline Execution Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"Error during ETL execution: {e}")
        raise
    finally:
        etl.close()


if __name__ == "__main__":
    main()