import os
from google import genai
from google.genai import types
import yfinance as yf

def get_stock_fundamentals(ticker_symbol: str):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    
    data = {
        "short_name": info.get("shortName", ticker_symbol),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "forward_pe": info.get("forwardPE", "N/A"),
        "dividend_yield": info.get("dividendYield", "N/A"),
        "beta": info.get("beta", "N/A"),
        "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
        "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        "recent_income_statement": income_stmt.iloc[:, :3].to_string() if not income_stmt.empty else "N/A",
        "recent_balance_sheet": balance_sheet.iloc[:, :3].to_string() if not balance_sheet.empty else "N/A"
    }
    return data

REPORT_SYSTEM_PROMPT = """
You are a senior institutional equity research analyst. Your task is to generate a comprehensive stock research report based on the provided financial metrics and data. 

You must strictly follow this exact structural format and use Markdown:

# Equity Research Report: [Company Name] ([Ticker])

## 1. Executive Summary & Verdict
- Core business summary
- High-level investment thesis
- Definitive stance (Bullish / Bearish / Neutral) with key conviction driver

## 2. Financial Performance & Balance Sheet Health
- Revenue and net income trajectory
- Margin analysis (Gross, Operating, Net)
- Balance sheet strength (Debt-to-Equity, liquidity, cash burn/generation)

## 3. Valuation & Market Context
- Current valuation multiples (P/E, EV/EBITDA, etc. vs historical/peers)
- Market sentiment and technical positioning (52-week range, beta)
- Risk/reward setup at current price

## 4. Key Risks & Bear Case
- Primary structural or macro risks threatening the thesis
- Downside catalysts

## 5. Final Investment Conclusion
- Actionable summary for capital allocation
"""

def generate_stock_report(ticker: str) -> str:
    stock_data = get_stock_fundamentals(ticker)
    api_key = os.environ.get("GEMINI_API_KEY") # Streamlit injects secrets into environment variables automatically
    client = genai.Client(api_key=api_key)
    
    user_prompt = f"""
    Generate the institutional research report for ticker: {ticker.upper()}
    Here is the live data extracted for the company:
    {stock_data}
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=REPORT_SYSTEM_PROMPT,
            temperature=0.2,
        )
    )
    
    return response.text
