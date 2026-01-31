import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.sslmode = os.getenv("DB_SSLMODE", "require")

    def get_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                sslmode=self.sslmode
            )
            return conn
        except psycopg2.Error as e:
            print(f"Connection failed: {e}")
            raise