import yfinance as yf
import pandas as pd

def get_fundamentals(stock: str) -> dict:
    """Return core fundamental metrics: market cap, P/E, EPS, profit margin."""
    t = yf.Ticker(stock)
    info = t.info

    return {
        "symbol": stock.upper(),
        "company_name": info.get("longName"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "eps_ttm": info.get("trailingEps"),
        "dividend_yield": info.get("dividendYield"),
        "profit_margin": info.get("profitMargins"),  # 0.25 = 25%
    }

def get_income_statement(stock: str) -> pd.DataFrame:
    """Return full income statement DF (Revenue, Net Income etc.)."""
    t = yf.Ticker(stock)
    return t.financials  # columns = years, rows = metrics

def get_revenue_growth_yoy(stock: str) -> float | None:
    """Calculate YoY revenue growth from income statement."""
    df = get_income_statement(stock)
    if df is None or "Total Revenue" not in df.index or len(df.columns) < 2:
        return None
    latest = df.loc["Total Revenue", df.columns[0]]
    prev = df.loc["Total Revenue", df.columns[1]]
    if prev == 0:
        return None
    return float(((latest - prev) / prev) * 100)

def get_net_margin_trend(stock: str) -> float | None:
    """Return YoY change in profit margin."""
    df = get_income_statement(stock)
    if df is None or "Net Income" not in df.index or "Total Revenue" not in df.index or len(df.columns) < 2:
        return None

    latest_margin = df.loc["Net Income", df.columns[0]] / df.loc["Total Revenue", df.columns[0]]
    prev_margin = df.loc["Net Income", df.columns[1]] / df.loc["Total Revenue", df.columns[1]]
    return float((latest_margin - prev_margin) * 100)  # in %
