import psycopg2
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
try:
    cur.execute("SELECT * FROM llm_provider_model;")
    colnames = [desc[0] for desc in cur.description]
    print(colnames)
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(e)
