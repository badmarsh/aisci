import psycopg2
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
try:
    conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/onyx")
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'llm_provider';
    """)
    print("Columns in onyx.llm_provider:")
    for row in cur.fetchall():
        print(" - " + row[0])
except Exception as e:
    print("Error connecting to onyx DB:", e)

try:
    conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'llm_provider';
    """)
    print("Columns in postgres.llm_provider:")
    for row in cur.fetchall():
        print(" - " + row[0])
except Exception as e:
    print("Error connecting to postgres DB:", e)
