import psycopg2
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%model%' OR table_name LIKE '%config%');")
print("Tables containing 'model' or 'config':")
for row in cur.fetchall():
    print(row[0])
