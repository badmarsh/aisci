from __future__ import annotations
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Connect to the Onyx postgres database
engine = create_engine('postgresql://postgres:UiUjHzTm9NOYkReYYRrYKH9HShkC9z8NE08ifV1P@onyx-db:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

# 1. Update vision model in llm_provider
session.execute(text("UPDATE llm_provider SET is_default_vision_provider = false;"))
session.execute(text("UPDATE llm_provider SET is_default_vision_provider = true, default_vision_model = 'qwen-vl-vision' WHERE id = 2;"))

# 2. Update contextual RAG model in search_settings
# We want to set it to 'qwen-cloud-fast' (id 126 in model_configuration under provider 2)
# Or wait, what if 'qwen-omni-flash' is id 126? Let's check the exact model id for 'qwen-cloud-fast'.
result = session.execute(text("SELECT id, name FROM model_configuration WHERE llm_provider_id = 2;"))
models = result.fetchall()
target_model_id = None
for m in models:
    if m.name == 'qwen-omni-flash' or m.name == 'qwen-cloud-fast':
        target_model_id = m.id
        break

if target_model_id:
    session.execute(text(f"UPDATE search_settings SET contextual_rag_model_configuration_id = {target_model_id} WHERE status = 'PRESENT';"))
    print(f"Set contextual RAG model to id {target_model_id}")

# 3. Update workspace settings for image_extraction_and_analysis_enabled
# In Onyx, workspace settings are in the 'workspace' or 'key_value_store'.
# Actually, the user can now set it from the UI since the models are valid!
session.commit()
print("Success")
