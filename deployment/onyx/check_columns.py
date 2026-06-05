import psycopg2
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE column_name LIKE '%fallback%';")
print("Fallback columns:")
print(cur.fetchall())

cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE column_name LIKE '%model%';")
print("\nModel columns:")
for row in cur.fetchall():
    print(row)
