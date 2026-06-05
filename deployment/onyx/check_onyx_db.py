import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
try:
    conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/onyx")
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    print("Tables in onyx db:")
    print([r[0] for r in cur.fetchall()])
except Exception as e:
    print(f"Error connecting to onyx DB: {e}")
