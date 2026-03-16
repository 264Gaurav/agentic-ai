# tracking/mlflow_tracker.py
# ─────────────────────────────────────────────────────────────
# MLflow tracking via DagsHub remote.
#
# What gets tracked per chat() call:
#   PARAMS    → model, temperature, thread_id, tools bound
#   METRICS   → latency_ms, tool_call_count, response_length,
#               input_tokens_est, output_tokens_est
#   TAGS      → tools_used, status (success/error)
#   ARTIFACTS → input_message.txt, output_message.txt,
#               conversation.json
# ─────────────────────────────────────────────────────────────

import time
import json
import dagshub
import mlflow
from config.settings import (
    DAGSHUB_REPO_OWNER,
    DAGSHUB_REPO_NAME,
    MLFLOW_EXPERIMENT,
    LLM_MODEL,
    LLM_TEMPERATURE,
)
from tools import ALL_TOOLS


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return max(1, len(text) // 4)


def _extract_tool_calls(messages: list) -> list[str]:
    """Pull tool names actually invoked from message history."""
    tools_used = []
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                if name and name not in tools_used:
                    tools_used.append(name)
    return tools_used


def setup_mlflow():
    """
    Initialise DagsHub and point MLflow at the remote tracking server.
    Call once at application startup (StockAgent.__init__).
    Requires DAGSHUB_USER_TOKEN in .env  OR  interactive login on first run.
    """
    dagshub.init(
        repo_owner=DAGSHUB_REPO_OWNER,
        repo_name=DAGSHUB_REPO_NAME,
        mlflow=True,
    )
    mlflow.set_experiment(MLFLOW_EXPERIMENT)


class MLflowTracker:
    """
    Context-manager that wraps a single chat() call with an MLflow run.

    Usage (inside agent.py):
        with MLflowTracker(user_message, thread_id) as tracker:
            reply, messages = ...
            tracker.finish(reply, messages)
    """

    def __init__(self, user_message: str, thread_id: str):
        self.user_message = user_message
        self.thread_id    = thread_id
        self._run         = None
        self._start_ms    = None

    def __enter__(self):
        self._run = mlflow.start_run(
            run_name=f"thread-{self.thread_id}",
            tags={
                "thread_id": self.thread_id,
                "model":     LLM_MODEL,
            },
        )
        self._start_ms = time.time()

        mlflow.log_params({
            "model":       LLM_MODEL,
            "temperature": LLM_TEMPERATURE,
            "thread_id":   self.thread_id,
            "tools_bound": ", ".join(t.name for t in ALL_TOOLS),
        })
        mlflow.log_text(self.user_message, "input_message.txt")
        return self

    def finish(self, reply: str, all_messages: list, error: str | None = None):
        """Log metrics, tags, and artifacts after the agent responds."""
        elapsed_ms = (time.time() - self._start_ms) * 1000
        tools_used = _extract_tool_calls(all_messages)

        mlflow.log_metrics({
            "latency_ms":        round(elapsed_ms, 2),
            "tool_call_count":   len(tools_used),
            "response_length":   len(reply),
            "input_tokens_est":  _estimate_tokens(self.user_message),
            "output_tokens_est": _estimate_tokens(reply),
        })

        mlflow.set_tags({
            "tools_used": ", ".join(tools_used) if tools_used else "none",
            "has_error":  str(error is not None),
            "status":     "error" if error else "success",
        })

        mlflow.log_text(reply, "output_message.txt")
        mlflow.log_text(
            json.dumps({
                "thread_id":  self.thread_id,
                "input":      self.user_message,
                "output":     reply,
                "tools_used": tools_used,
                "latency_ms": round(elapsed_ms, 2),
                "messages": [
                    {
                        "type":    type(m).__name__,
                        "content": m.content if hasattr(m, "content") else str(m),
                    }
                    for m in all_messages
                ],
            }, indent=2),
            "conversation.json",
        )

        if error:
            mlflow.log_text(error, "error.txt")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._run:
            mlflow.end_run(status="FAILED" if exc_type else "FINISHED")
        return False
