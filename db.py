import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supa"]["url"]
    key = st.secrets["supa"]["key"]
    return create_client(url, key)

def fetch_archive():
    supabase = init_supabase()
    response = supabase.table("stock_archive").select("*").order("discovery_date", desc=True).execute()
    return response.data

def save_report_to_archive(data: dict, report_text: str):
    supabase = init_supabase()
    payload = {
        "ticker": data.get("ticker"),
        "short_name": data.get("short_name"),
        "sector": data.get("sector"),
        "industry": data.get("industry"),
        "market_cap": str(data.get("market_cap")),
        "pe_ratio": str(data.get("pe_ratio")),
        "report_markdown": report_text
    }
    # Upsert to prevent duplicate ticker entries on re-evaluation cycles
    supabase.table("stock_archive").upsert(payload, on_conflict="ticker").execute()
