import psycopg2
from pgvector.psycopg2 import register_vector
import os

def get_connection():
    print("Connection to PostgreSQL")
    try:
        conn = psycopg2.connect(
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],  
            port=os.environ["POSTGRES_PORT"]
        )
        register_vector(conn)  # Registra il tipo VECTOR per psycopg2
        cur = conn.cursor()
        print("Connection to DB success")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        exit()
    return conn, cur
