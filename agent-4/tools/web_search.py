# tools/web_search.py
# ─────────────────────────────────────────────────────────────
# Tool: tavily_search
#   Fallback web search for:
#   • Tickers not covered by get_stock_price
#   • Stock news, analyst opinions, company context
#   • "Should I buy?" type queries
# ─────────────────────────────────────────────────────────────
from langchain_tavily import TavilySearch
from config.settings import TAVILY_MAX_RESULTS

tavily_tool = TavilySearch(
    max_results=TAVILY_MAX_RESULTS,
    name="tavily_search",
    description=(
        "A real-time web search tool. Use this tool when:\n"
        "  1. get_stock_price fails or returns an error.\n"
        "  2. The ticker is not a standard US or Indian stock.\n"
        "  3. The user asks for stock news, company info, or analyst opinions.\n"
        "  4. You need to find the ticker symbol from a company name.\n"
        "  5. The user asks 'should I buy/sell' — search for recent context.\n"
        "Do NOT use this as the first choice for price lookup — prefer get_stock_price."
    ),
)
