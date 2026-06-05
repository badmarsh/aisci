import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT name, custom_config FROM llm_provider WHERE custom_config IS NOT NULL;")
for row in cur.fetchall():
    print("Provider:", row[0])
    print(json.dumps(row[1], indent=2))
