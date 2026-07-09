from langchain.agents import AgentState
from typing import get_type_hints
print(get_type_hints(AgentState, include_extras=True))
