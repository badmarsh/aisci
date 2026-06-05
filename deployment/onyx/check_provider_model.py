import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'llm_provider_model';")
print("Columns in llm_provider_model:")
for row in cur.fetchall():
    print(row[0])

cur.execute("SELECT * FROM llm_provider_model WHERE llm_provider_id = 5;")
colnames = [desc[0] for desc in cur.description]
print("\nRows in llm_provider_model for provider 5:")
for row in cur.fetchall():
    print(dict(zip(colnames, row)))
