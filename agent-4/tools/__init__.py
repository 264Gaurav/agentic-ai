from .stock_price import get_stock_price
from .web_search import tavily_tool

# All tools exposed to the LLM agent
ALL_TOOLS = [get_stock_price, tavily_tool]
