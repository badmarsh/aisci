import psycopg2
import os

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database;")
for row in cur.fetchall():
    print(row[0])
