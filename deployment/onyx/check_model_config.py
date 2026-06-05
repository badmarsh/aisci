import psycopg2
import json
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'model_configuration';")
print("Columns in model_configuration:")
for row in cur.fetchall():
    print(row[0])

cur.execute("SELECT * FROM model_configuration;")
colnames = [desc[0] for desc in cur.description]
print("\nRows in model_configuration:")
for row in cur.fetchall():
    row_dict = dict(zip(colnames, row))
    print(json.dumps(row_dict, indent=2, default=str))
