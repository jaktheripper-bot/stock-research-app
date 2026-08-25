import streamlit as st
from analyzer import generate_stock_report

st.set_page_config(page_title="Institutional Stock Analyzer", layout="wide")

st.title("Automated Equity Research Terminal")
st.markdown("Input any stock ticker to generate a standardized institutional-grade research breakdown.")

ticker_input = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA):", "").upper()

if st.button("Generate Research Report"):
    if not ticker_input:
        st.warning("Please enter a valid ticker symbol.")
    else:
        with st.spinner(f"Fetching fundamentals and analyzing {ticker_input}..."):
            try:
                report = generate_stock_report(ticker_input)
                st.markdown("---")
                st.markdown(report)
            except Exception as e:
                st.error(f"Error generating report: {e}")
