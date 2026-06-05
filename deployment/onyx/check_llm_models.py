import sys
sys.path.insert(0, '/app')
from onyx.db.engine import get_sqlalchemy_engine
from sqlalchemy.orm import Session
from onyx.db.models import LLMProvider

engine = get_sqlalchemy_engine()
session = Session(engine)
for p in session.query(LLMProvider).all():
    print(f'Provider ID: {p.id}, Provider Name: {p.name}, Provider Type: {p.provider}')
    for m in p.llm_models:
        print(f'  - model_name: {m.model_name}, display_model_name: {m.display_model_name}')
