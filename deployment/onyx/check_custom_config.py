import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT name, custom_config FROM llm_provider;")
print("LLM Providers custom configs:")
for row in cur.fetchall():
    print(f"Provider: {row[0]}, custom_config: {row[1]}")
