import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:UiUjHzTm9NOYkReYYRrYKH9HShkC9z8NE08ifV1P@onyx-db:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

result = session.execute(text("SELECT value FROM key_value_store WHERE key='onyx_settings';"))
row = result.fetchone()
if row:
    val = row[0]
    if isinstance(val, str):
        val = json.loads(val)
    val['image_extraction_and_analysis_enabled'] = True
    val['image_analysis_max_size_mb'] = 20
    new_val = json.dumps(val)
    session.execute(text("UPDATE key_value_store SET value = :val WHERE key='onyx_settings';"), {"val": new_val})
    session.commit()
    print("Updated onyx_settings JSON")
else:
    print("onyx_settings key not found")
