import sqlalchemy
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:UiUjHzTm9NOYkReYYRrYKH9HShkC9z8NE08ifV1P@onyx-db:5432/postgres')
with engine.connect() as conn:
    res = conn.execute(text("SELECT table_name FROM information_schema.columns WHERE column_name = 'access_type' AND table_schema = 'public';"))
    tables = [r[0] for r in res.fetchall()]
    for table in tables:
        res = conn.execute(text(f"SELECT access_type, count(*) FROM {table} GROUP BY access_type;"))
        print(f'{table}.access_type:', res.fetchall())


