import os
import requests
import streamlit as st
from google import genai
import yfinance as yf

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

@st.cache_data(ttl=3600)
def get_stock_fundamentals(ticker_symbol: str):
    stock = yf.Ticker(ticker_symbol, session=session)
    info = stock.info
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    
    data = {
        "short_name": info.get("shortName", ticker_symbol),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "recent_income_statement": income_stmt.iloc[:5, :1].to_string() if not income_stmt.empty else "N/A",
        "recent_balance_sheet": balance_sheet.iloc[:5, :1].to_string() if not balance_sheet.empty else "N/A"
    }
    return data

REPORT_SYSTEM_PROMPT = """
You are an equity research analyst. Your task is to generate a comprehensive stock research report based on the provided financial metrics and data. 
You must strictly follow this exact structural format and use Markdown:
# Equity Research Report: [Company Name] ([Ticker])
## 1. Executive Summary & Verdict
## 2. Financial Performance & Balance Sheet Health
## 3. Valuation & Market Context
## 4. Key Risks & Bear Case
## 5. Final Investment Conclusion
"""

def generate_stock_report(ticker: str) -> str:
    stock_data = get_stock_fundamentals(ticker)
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    user_prompt = f"Generate the research report for ticker: {ticker.upper()}\nLive data:\n{stock_data}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=REPORT_SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )
    return response.text
