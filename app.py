import os
import streamlit as st
from analyzer import generate_stock_report

st.set_page_config(page_title="Stock Research Terminal", layout="wide")
st.title("Automated Equity Research Terminal")

api_key = st.secrets.get("GEMINI_API_KEY")
ticker_input = st.text_input("Enter Stock Ticker (e.g., AAPL):", "").upper()

if st.button("Generate Research Report"):
    if not api_key:
        st.error("Gemini API key is missing.")
    elif not ticker_input:
        st.warning("Please enter a valid ticker.")
    else:
        with st.spinner(f"Analyzing {ticker_input}..."):
            try:
                report_text = generate_stock_report(ticker_input)
                st.markdown(report_text)
            except Exception as e:
                st.error(f"Error generating report: {e}")
