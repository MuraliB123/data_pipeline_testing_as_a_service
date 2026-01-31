from utils.db_connection import DatabaseConnection

if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Create 'hello' table
        create_table_query = """
        CREATE TABLE hello (
            id INT IDENTITY(1,1) PRIMARY KEY,
            message NVARCHAR(255) NOT NULL
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        print("Table 'hello' created successfully!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")