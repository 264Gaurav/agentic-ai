# agent.py
# ─────────────────────────────────────────────────────────────
# Thin helper around the compiled graph.
# Manages thread configs and exposes a clean `chat()` interface.
# ─────────────────────────────────────────────────────────────

from graph.builder import build_graph


class StockAgent:
    """
    Wraps the LangGraph agent with a simple chat interface.

    Usage:
        agent = StockAgent()
        reply = agent.chat("Buy 10 AMZN at current price. Total cost?", thread_id="1")
        print(reply)
    """

    def __init__(self, visualize: bool = False):
        self.graph = build_graph(visualize=visualize)

    def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a message on a given thread and return the assistant's reply.

        Args:
            message:   User message text.
            thread_id: Conversation thread ID (memory is scoped per thread).

        Returns:
            Assistant's response as a string.
        """
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
        )
        return state["messages"][-1].content
