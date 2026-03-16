# agent.py
# ─────────────────────────────────────────────────────────────
# StockAgent wraps the compiled LangGraph with:
#   • a clean chat() interface
#   • MLflow tracking on every call (latency, tools, tokens)
# ─────────────────────────────────────────────────────────────

from graph.builder import build_graph
from tracking import MLflowTracker, setup_mlflow


class StockAgent:
    """
    Wraps the LangGraph agent with MLflow-tracked chat interface.

    Usage:
        agent = StockAgent()
        reply = agent.chat("Buy 10 AMZN at current price. Total?", thread_id="1")
        print(reply)
    """

    def __init__(self, visualize: bool = False):
        setup_mlflow()                          # configure URI + experiment once
        self.graph = build_graph(visualize=visualize)

    def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a message on a thread, log the run to MLflow, return reply.

        Args:
            message:   User message text.
            thread_id: Scopes conversation memory.

        Returns:
            Assistant's response as a string.
        """
        config = {"configurable": {"thread_id": thread_id}}

        with MLflowTracker(message, thread_id) as tracker:
            try:
                state = self.graph.invoke(
                    {"messages": [{"role": "user", "content": message}]},
                    config=config,
                )
                reply    = state["messages"][-1].content
                all_msgs = state["messages"]
                tracker.finish(reply, all_msgs)
                return reply

            except Exception as e:
                tracker.finish("", [], error=str(e))
                raise
