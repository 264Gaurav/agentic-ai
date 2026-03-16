# graph/nodes.py
# ─────────────────────────────────────────────────────────────
# Chatbot node: invokes the LLM with all bound tools.
# The LLM decides whether to call a tool or reply directly.
# ─────────────────────────────────────────────────────────────

from langchain.chat_models import init_chat_model
from config.settings import LLM_MODEL
from tools import ALL_TOOLS
from graph.state import State


# Initialise LLM once and bind all tools
# _llm = init_chat_model(LLM_MODEL)
from langchain_ollama import ChatOllama  
_llm = ChatOllama(model=LLM_MODEL, temperature=0)

_llm_with_tools = _llm.bind_tools(ALL_TOOLS)


def chatbot_node(state: State) -> dict:
    """
    Core LLM node. Receives the current state (message history),
    calls the LLM, and returns the new assistant message.
    """
    response = _llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
