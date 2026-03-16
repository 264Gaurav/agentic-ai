# graph/state.py
# ─────────────────────────────────────────────────────────────
# LangGraph State — shared across all nodes in the graph.
# add_messages appends to the list instead of overwriting.
# ─────────────────────────────────────────────────────────────

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
