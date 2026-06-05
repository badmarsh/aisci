import psycopg2
import os
import json

password = os.environ.get("POSTGRES_PASSWORD", "password")
conn = psycopg2.connect(f"postgresql://postgres:{password}@onyx-db:5432/postgres")
cur = conn.cursor()
cur.execute("""
    SELECT f.llm_model_flow_type, f.is_default, m.name, m.model_name
    FROM llm_model_flow f
    JOIN model_configuration m ON f.model_configuration_id = m.id
    ORDER BY f.llm_model_flow_type;
""")
rows = cur.fetchall()
for r in rows:
    print(r)
