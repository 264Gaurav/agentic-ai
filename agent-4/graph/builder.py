# graph/builder.py
# ─────────────────────────────────────────────────────────────
# Assembles the LangGraph:
#   START → chatbot ⇄ tools (loop until done) → END
# Compiles with MemorySaver for per-thread conversation memory.
# ─────────────────────────────────────────────────────────────

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from graph.state import State
from graph.nodes import chatbot_node
from tools import ALL_TOOLS


def build_graph(visualize: bool = False):
    """
    Build and compile the agent graph.

    Args:
        visualize: If True, display the graph diagram (Jupyter only).

    Returns:
        Compiled LangGraph ready to invoke.
    """
    builder = StateGraph(State)

    # ── Nodes ────────────────────────────────────────────────
    builder.add_node("chatbot", chatbot_node)
    builder.add_node("tools",   ToolNode(ALL_TOOLS))

    # ── Edges ────────────────────────────────────────────────
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)  # tool call or end?
    builder.add_edge("tools", "chatbot")                       # loop back after tool

    # ── Compile ──────────────────────────────────────────────
    graph = builder.compile(checkpointer=MemorySaver())

    if visualize:
        try:
            from IPython.display import Image, display
            display(Image(graph.get_graph().draw_mermaid_png()))
        except Exception:
            print("[visualize] Could not render graph. Are you in a Jupyter notebook?")

    return graph
