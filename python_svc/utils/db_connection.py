import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.server = os.getenv("SERVER")
        self.database = os.getenv("DATABASE")
        self.trusted_connection = os.getenv("TRUSTED_CONNECTION", "yes")
        self.trust_server_certificate = os.getenv("TRUST_SERVER_CERTIFICATE", "yes")

    def get_connection(self):
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Trusted_Connection={self.trusted_connection};"
            f"TrustServerCertificate={self.trust_server_certificate};"
        )
        try:
            conn = pyodbc.connect(connection_string)
            return conn
        except pyodbc.Error as e:
            print(f"Connection failed: {e}")
            raise