import os
import requests
import streamlit as st
from google import genai
from normalizer import normalize_stock_data

@st.cache_data(ttl=3600)
def get_stock_fundamentals(query: str):
    api_key = st.secrets.get("TWELVE_DATA_API_KEY", "demo")
    
    search_url = f"https://api.twelvedata.com/symbol_search?symbol={query}&apikey={api_key}"
    response = requests.get(search_url)
    response.raise_for_status()
    result = response.json()
    
    if "code" in result and result["code"] != 200:
        raise ValueError(f"Twelve Data API Error: {result.get('message', 'Unknown error')}")
    
    matches = result.get("data", [])
    if not matches:
        raise ValueError(f"Could not find a valid ticker for '{query}'.")
        
    ticker_symbol = matches[0]["symbol"]
    exchange = matches[0].get("exchange", "NSE")
    
    for match in matches:
        if match.get("exchange") in ["NSE", "BSE"]:
            ticker_symbol = match["symbol"]
            exchange = match["exchange"]
            break

    profile_res = requests.get(f"https://api.twelvedata.com/profile?symbol={ticker_symbol}&apikey={api_key}").json()
    stats_res = requests.get(f"https://api.twelvedata.com/statistics?symbol={ticker_symbol}&apikey={api_key}").json()
    
    valuations = stats_res.get("statistics", {}).get("valuations_metrics", {})
    
    raw_data = {
        "ticker": ticker_symbol,
        "short_name": profile_res.get("name", ticker_symbol),
        "sector": profile_res.get("sector", "N/A"),
        "industry": profile_res.get("industry", "N/A"),
        "market_cap": profile_res.get("market_capitalization", "N/A"),
        "pe_ratio": valuations.get("trailing_pe", "N/A"),
        "description": profile_res.get("description", "N/A")
    }
    
    # Apply normalization to prevent LLM currency confusion
    return normalize_stock_data(raw_data, exchange=exchange)

REPORT_SYSTEM_PROMPT = """
You are an equity research analyst. Generate a comprehensive stock research report based on the provided metrics using strict Markdown. 
All financial figures provided are in Indian Rupees (INR) unless explicitly stated otherwise. Express market values in Crores (Cr).
"""

def generate_stock_report(ticker: str) -> str:
    stock_data = get_stock_fundamentals(ticker)
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    user_prompt = f"Generate the research report for: {stock_data.get('short_name')} ({stock_data.get('ticker')})\nData: {stock_data}"
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=REPORT_SYSTEM_PROMPT
        ),
    )
    return response.text
