# main.py
# ─────────────────────────────────────────────────────────────
# Entry point — run all example conversations.
# ─────────────────────────────────────────────────────────────

from dotenv import load_dotenv
load_dotenv()

from agent import StockAgent


def run_examples():
    agent = StockAgent(visualize=False)  # set True in Jupyter to see graph diagram

    print("=" * 60)

    # ── Thread 1: Multi-turn memory (US + Indian stocks) ─────
    print("\n[Thread 1 — Message 1]")
    reply = agent.chat(
        "I want to buy 20 AMZN and 15 MSFT at current prices. What is the total cost?",
        thread_id="1",
    )
    print(reply)

    print("\n[Thread 1 — Message 2]  (remembers previous total)")
    reply = agent.chat(
        "Now add 10 RIL stocks at current price. What's the new grand total?",
        thread_id="1",
    )
    print(reply)

    print("=" * 60)

    # ── Thread 2: Unlisted ticker → Tavily fallback ───────────
    print("\n[Thread 2 — Unlisted ticker fallback]")
    reply = agent.chat(
        "What is the current stock price of Zomato?",
        thread_id="2",
    )
    print(reply)

    print("=" * 60)

    # ── Thread 3: News + opinion → Tavily search ─────────────
    print("\n[Thread 3 — News & opinion query]")
    reply = agent.chat(
        "What's the latest news about Tesla stock? Should I buy it today?",
        thread_id="3",
    )
    print(reply)

    print("=" * 60)

    # ── Thread 4: Lookup by company name (not ticker) ─────────
    print("\n[Thread 4 — Company name lookup]")
    reply = agent.chat(
        "What is the current stock price of Reliance Industries?",
        thread_id="4",
    )
    print(reply)

    print("=" * 60)


if __name__ == "__main__":
    run_examples()
