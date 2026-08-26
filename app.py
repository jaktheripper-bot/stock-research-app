import streamlit as st

# Initialize page first so Streamlit can render UI elements
st.set_page_config(page_title="Diagnostic Mode", layout="wide")

try:
    import os
    from openai import OpenAI
    import pandas as pd
    import yfinance as yf
    from analyzer import generate_stock_report
    
    st.success("All imports passed. The crash is happening further down.")
    
    st.title("Automated Equity Research Terminal")
    api_key = st.secrets.get("OPENAI_API_KEY")
    
    ticker_input = st.text_input("Enter Stock Ticker:", "").upper()
    
    if st.button("Generate Research Report"):
        if not api_key:
            st.error("OpenAI API key is missing.")
        elif not ticker_input:
            st.warning("Please enter a valid ticker.")
        else:
            with st.spinner("Analyzing..."):
                report_text = generate_stock_report(ticker_input)
                st.markdown(report_text)
                
except Exception as e:
    st.error(f"Fatal Startup Error: {e}")
    st.exception(e)
