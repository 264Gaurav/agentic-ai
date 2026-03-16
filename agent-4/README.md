# Stock Agent

## Agent with Memory i.e., it will save the previous conversation and states of a chat thread (thread no. wise)


A modular LangGraph-powered stock agent with real-time price lookup and Tavily web search fallback.

## Project Structure

```
agent-4/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # LLM model, API URLs, Indian ticker map
│
├── tools/
│   ├── __init__.py           # Exports ALL_TOOLS list
│   ├── stock_price.py        # get_stock_price tool (US + Indian)
│   └── web_search.py         # tavily_search tool (fallback + news)
│
├── graph/
│   ├── __init__.py
│   ├── state.py              # LangGraph State (message history)
│   ├── nodes.py              # chatbot_node (LLM + tools)
│   └── builder.py            # build_graph() — wires nodes/edges
│
├── agent.py                  # StockAgent class (clean chat interface)
├── main.py                   # Entry point — example conversations
├── requirements.txt
└── .env                      # GOOGLE_API_KEY, TAVILY_API_KEY
```

## Tool Decision Logic

```
User asks for stock price
        │
        ▼
  get_stock_price
   ├── Indian ticker? → yfinance (NSE)
   ├── US ticker?     → stockprices.dev (no API key)
   └── Error / not found
        │
        ▼
  tavily_search  ← also used directly for news/opinions
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Run

```bash
python main.py
```

## Adding a New Tool

1. Create `tools/my_tool.py` with a `@tool`-decorated function
2. Import it in `tools/__init__.py` and add to `ALL_TOOLS`
3. That's it — the agent will automatically have access to it
