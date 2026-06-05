import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT * FROM llm_model_flow;")
colnames = [desc[0] for desc in cur.description]
for row in cur.fetchall():
    print(dict(zip(colnames, row)))
