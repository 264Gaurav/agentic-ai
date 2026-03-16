# config/settings.py
# ─────────────────────────────────────────────────────────────
# Central config: ticker maps, API endpoints, model name, etc.
# ─────────────────────────────────────────────────────────────

# LLM model to use
# LLM_MODEL = "google_genai:gemini-2.0-flash"
LLM_MODEL = "llama3.1:8b" 

# stockprices.dev base URL (no API key needed)
STOCK_API_BASE = "https://stockprices.dev/api"

# Request timeout (seconds)
REQUEST_TIMEOUT = 5

# Tavily max results
TAVILY_MAX_RESULTS = 5

# Map of short Indian ticker names → yfinance NSE symbols
INDIAN_TICKERS: dict[str, str] = {
    "RIL":        "RELIANCE.NS",
    "TCS":        "TCS.NS",
    "INFY":       "INFY.NS",
    "WIPRO":      "WIPRO.NS",
    "HDFCBANK":   "HDFCBANK.NS",
    "ICICIBANK":  "ICICIBANK.NS",
    "SBIN":       "SBIN.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "ADANIENT":   "ADANIENT.NS",
    "ZOMATO":     "ZOMATO.NS",
    "NYKAA":      "FSN.NS",
    "PAYTM":      "PAYTM.NS",
    "ONGC":       "ONGC.NS",
    "COALINDIA":  "COALINDIA.NS",
}
