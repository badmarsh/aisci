import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT name, model_configurations FROM llm_provider;")
rows = cur.fetchall()
for row in rows:
    name, config = row
    print(f"Provider: {name}")
    if config:
        for c in config:
            if 'qwen-fast' in c.get('name', ''):
                print("==== FOUND qwen-fast ====")
                print(json.dumps(c, indent=2))
            if 'gemini' in str(c).lower():
                print("==== FOUND gemini in model ====")
                print(json.dumps(c, indent=2))
