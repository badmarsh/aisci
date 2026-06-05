import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT id, name, custom_config FROM llm_provider WHERE id=5;")
print("Provider 5:")
print(cur.fetchall())
