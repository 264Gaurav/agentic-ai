# tools/stock_price.py
# ─────────────────────────────────────────────────────────────
# Tool: get_stock_price
#   • US stocks / ETFs  → stockprices.dev  (no API key)
#   • Indian stocks     → yfinance via NSE ticker map
#   • On failure        → hints agent to fall back to tavily_search
# ─────────────────────────────────────────────────────────────

import requests
from langchain_core.tools import tool
from config.settings import INDIAN_TICKERS, STOCK_API_BASE, REQUEST_TIMEOUT


def _fetch_indian_price(ticker: str) -> dict:
    """Fetch NSE stock price using yfinance."""
    try:
        import yfinance as yf
        resolved = INDIAN_TICKERS[ticker]
        info = yf.Ticker(resolved).fast_info
        price = info.last_price

        if price is None:
            return {
                "error": (
                    f"yfinance returned no price for '{ticker}' ({resolved}). "
                    "Use tavily_search to find the current price."
                )
            }

        return {
            "ticker":        ticker,
            "resolved":      resolved,
            "current_price": round(float(price), 2),
            "currency":      "INR",
            "source":        "yfinance (NSE)",
        }

    except ImportError:
        return {"error": "yfinance is not installed. Run: pip install yfinance"}
    except Exception as e:
        return {
            "error": (
                f"yfinance error for '{ticker}': {e}. "
                "Use tavily_search as fallback."
            )
        }


def _fetch_us_price(ticker: str) -> dict:
    """Fetch US stock or ETF price from stockprices.dev."""
    endpoints = [
        f"{STOCK_API_BASE}/stocks/{ticker}",
        f"{STOCK_API_BASE}/etfs/{ticker}",   # fallback for ETFs
    ]

    for url in endpoints:
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "ticker":        data.get("Ticker", ticker),
                    "name":          data.get("Name", ""),
                    "current_price": data.get("Price"),
                    "change_amount": data.get("ChangeAmount"),
                    "change_pct":    data.get("ChangePercentage"),
                    "currency":      "USD",
                    "source":        "stockprices.dev (real-time)",
                }
        except requests.exceptions.Timeout:
            return {
                "error": (
                    f"Request timed out for '{ticker}'. "
                    "Use tavily_search to find the current price."
                )
            }
        except Exception as e:
            return {
                "error": (
                    f"Unexpected error fetching '{ticker}': {e}. "
                    "Use tavily_search as fallback."
                )
            }

    return {
        "error": (
            f"Ticker '{ticker}' not found on stockprices.dev. "
            "Use tavily_search to find the current price."
        )
    }


@tool
def get_stock_price(ticker: str) -> dict:
    """
    Fetches the real-time current stock price for a given ticker symbol.

    Routing:
    - Indian stocks (RIL, TCS, INFY, WIPRO, etc.) → yfinance via NSE
    - US stocks & ETFs (AMZN, MSFT, AAPL, VOO, etc.) → stockprices.dev API

    Returns: ticker, current_price, currency, change info, and data source.

    IMPORTANT: Use this tool FIRST for any stock price query.
    If this tool returns an error, fall back to tavily_search.
    """
    ticker = ticker.upper().strip()

    if ticker in INDIAN_TICKERS:
        return _fetch_indian_price(ticker)

    return _fetch_us_price(ticker)
