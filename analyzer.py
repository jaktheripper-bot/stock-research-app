import os
import requests
import streamlit as st
from google import genai

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
    for match in matches:
        if match.get("exchange") in ["NSE", "BSE"]:
            ticker_symbol = match["symbol"]
            break

    profile_res = requests.get(f"https://api.twelvedata.com/profile?symbol={ticker_symbol}&apikey={api_key}").json()
    stats_res = requests.get(f"https://api.twelvedata.com/statistics?symbol={ticker_symbol}&apikey={api_key}").json()
    
    valuations = stats_res.get("statistics", {}).get("valuations_metrics", {})
    
    data = {
        "short_name": profile_res.get("name", ticker_symbol),
        "sector": profile_res.get("sector", "N/A"),
        "industry": profile_res.get("industry", "N/A"),
        "market_cap": profile_res.get("market_capitalization", "N/A"),
        "pe_ratio": valuations.get("trailing_pe", "N/A"),
        "description": profile_res.get("description", "N/A")
    }
    return data

REPORT_SYSTEM_PROMPT = """
You are an equity research analyst. Generate a comprehensive stock research report based on the provided metrics and data using strict Markdown.
"""

def generate_stock_report(ticker: str) -> str:
    stock_data = get_stock_fundamentals(ticker)
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    user_prompt = f"Generate the research report for: {stock_data.get('short_name')} ({ticker.upper})}\nData: {stock_data}"
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=REPORT_SYSTEM_PROMPT
        ),
    )
    return response.text
