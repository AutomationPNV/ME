import psycopg2
import os

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'motors'),
            user=os.getenv('POSTGRES_USER', 'admin'),
            password=os.getenv('POSTGRES_PASSWORD', 'admin')
        )
        return conn
    except Exception as e:
        print(f"Помилка підключення до БД: {e}")
        return None
