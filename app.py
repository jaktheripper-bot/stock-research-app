import os
from google import genai
from google.genai import types
import pandas as pd
import streamlit as st
import yfinance as yf
from analyzer import generate_stock_report

st.set_page_config(
    page_title="Stock Research Terminal",
    layout="wide",
)

st.title("Automated Equity Research Terminal")
st.markdown(
    "Input any stock ticker to generate a structured financial research breakdown."
)

st.markdown(
    "> **Disclaimer:** These reports are generated for educational purposes only "
    "and should not be construed as professional investment advice, financial planning, "
    "or recommendations to buy or sell securities."
)

api_key = st.secrets.get("GEMINI_API_KEY")

ticker_input = st.text_input(
    "Enter Stock Ticker (e.g., AAPL, MSFT, TSLA):", ""
).upper()

if st.button("Generate Research Report"):
  if not api_key:
    st.error(
        "Gemini API key is missing. Please configure it in your Streamlit"
        " Cloud settings."
    )
  elif not ticker_input:
    st.warning("Please enter a valid ticker symbol.")
  else:
    with st.spinner(f"Fetching fundamentals and analyzing {ticker_input}..."):
      try:
        report_text = generate_stock_report(ticker_input)
        
        st.markdown("---")
        st.markdown(report_text)
        
        st.download_button(
            label="Download Report as Text File",
            data=report_text,
            file_name=f"{ticker_input}_research_report.md",
            mime="text/markdown",
        )
        
      except Exception as e:
        st.error(f"Error generating report: {e}")
