# evaluation/evaluator.py
# ─────────────────────────────────────────────────────────────
# Offline evaluation of the stock agent using MLflow evaluate().
#
# Scores each response on:
#   - relevance    : does the answer address the question?
#   - correctness  : are numbers/facts present and consistent?
#   - tool_usage   : did the agent use the right tool(s)?
#   - conciseness  : is the response focused and not padded?
#
# Results are logged to a dedicated MLflow experiment so you
# can compare runs side-by-side in the MLflow UI.
# ─────────────────────────────────────────────────────────────

import re
import json
import mlflow
import pandas as pd
from typing import Any
from config.settings import MLFLOW_EXPERIMENT, LLM_MODEL


# ── Heuristic scorers (0.0 – 1.0) ────────────────────────────

def _score_relevance(question: str, answer: str) -> float:
    """Check if key question words appear in the answer."""
    q_words = set(re.findall(r"\b\w{4,}\b", question.lower()))
    a_words = set(re.findall(r"\b\w{4,}\b", answer.lower()))
    if not q_words:
        return 0.5
    overlap = len(q_words & a_words) / len(q_words)
    return round(min(overlap * 2, 1.0), 3)   # generous scaling


def _score_correctness(answer: str, expected_keywords: list[str]) -> float:
    """Fraction of expected keywords/values found in the answer."""
    if not expected_keywords:
        return 1.0
    found = sum(1 for kw in expected_keywords if kw.lower() in answer.lower())
    return round(found / len(expected_keywords), 3)


def _score_tool_usage(tools_used: list[str], expected_tools: list[str]) -> float:
    """Did the agent call the tools we expected?"""
    if not expected_tools:
        return 1.0
    matched = sum(1 for t in expected_tools if t in tools_used)
    return round(matched / len(expected_tools), 3)


def _score_conciseness(answer: str) -> float:
    """Penalise very short (<20 words) or very long (>300 words) answers."""
    word_count = len(answer.split())
    if word_count < 20:
        return 0.4
    if word_count > 300:
        return 0.6
    return 1.0


# ── Eval dataset ──────────────────────────────────────────────

EVAL_DATASET = [
    {
        "question":       "What is the current price of AAPL?",
        "expected_tools": ["get_stock_price"],
        "expected_kw":    ["AAPL", "$", "price"],
    },
    {
        "question":       "I want to buy 10 AMZN and 5 MSFT. What is the total cost?",
        "expected_tools": ["get_stock_price"],
        "expected_kw":    ["AMZN", "MSFT", "total"],
    },
    {
        "question":       "What is the current stock price of Reliance Industries?",
        "expected_tools": ["get_stock_price"],
        "expected_kw":    ["RIL", "INR", "price"],
    },
    {
        "question":       "What is the latest news about Tesla stock?",
        "expected_tools": ["tavily_search"],
        "expected_kw":    ["Tesla", "TSLA"],
    },
    {
        "question":       "What is the stock price of Zomato?",
        "expected_tools": ["get_stock_price", "tavily_search"],
        "expected_kw":    ["Zomato", "price"],
    },
]


# ── Main evaluator ────────────────────────────────────────────

class AgentEvaluator:
    """
    Run the eval dataset through the agent and log results to MLflow.

    Usage:
        from evaluation.evaluator import AgentEvaluator
        from agent import StockAgent

        evaluator = AgentEvaluator(StockAgent())
        evaluator.run()
    """

    def __init__(self, agent):
        self.agent = agent

    def _evaluate_one(self, sample: dict, thread_id: str) -> dict:
        """Run a single eval sample and return scores."""
        question        = sample["question"]
        expected_tools  = sample.get("expected_tools", [])
        expected_kw     = sample.get("expected_kw", [])

        # Run agent and capture full state for tool introspection
        config = {"configurable": {"thread_id": thread_id}}
        state  = self.agent.graph.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )
        answer     = state["messages"][-1].content
        all_msgs   = state["messages"]

        # Extract tools actually used
        tools_used = []
        for msg in all_msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    if name and name not in tools_used:
                        tools_used.append(name)

        # Score
        scores = {
            "relevance":    _score_relevance(question, answer),
            "correctness":  _score_correctness(answer, expected_kw),
            "tool_usage":   _score_tool_usage(tools_used, expected_tools),
            "conciseness":  _score_conciseness(answer),
        }
        scores["overall"] = round(sum(scores.values()) / len(scores), 3)

        return {
            "question":      question,
            "answer":        answer,
            "tools_used":    tools_used,
            "expected_tools":expected_tools,
            **scores,
        }

    def run(self, run_name: str = "evaluation"):
        """
        Evaluate all samples and log a summary run to MLflow.
        Prints a score table and returns the results DataFrame.
        """
        mlflow.set_experiment(f"{MLFLOW_EXPERIMENT}-eval")

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("model",          LLM_MODEL)
            mlflow.log_param("eval_samples",   len(EVAL_DATASET))

            results = []
            for i, sample in enumerate(EVAL_DATASET):
                print(f"  Evaluating [{i+1}/{len(EVAL_DATASET)}]: {sample['question'][:60]}...")
                result = self._evaluate_one(sample, thread_id=f"eval-{i}")
                results.append(result)

            df = pd.DataFrame(results)

            # ── Aggregate metrics ─────────────────────────────
            avg = df[["relevance","correctness","tool_usage","conciseness","overall"]].mean()
            mlflow.log_metrics({
                "avg_relevance":    round(avg["relevance"],    3),
                "avg_correctness":  round(avg["correctness"],  3),
                "avg_tool_usage":   round(avg["tool_usage"],   3),
                "avg_conciseness":  round(avg["conciseness"],  3),
                "avg_overall":      round(avg["overall"],      3),
            })

            # ── Log full results as artifact ──────────────────
            results_json = df.to_dict(orient="records")
            mlflow.log_text(
                json.dumps(results_json, indent=2),
                "eval_results.json",
            )
            mlflow.log_text(
                df.to_csv(index=False),
                "eval_results.csv",
            )

            # ── Print summary ─────────────────────────────────
            print("\n" + "=" * 60)
            print("EVALUATION SUMMARY")
            print("=" * 60)
            print(df[["question","overall","tool_usage","relevance"]].to_string(index=False))
            print("\nAVERAGES:")
            print(avg.to_string())
            print("=" * 60)

        return df
