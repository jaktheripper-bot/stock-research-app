def format_indian_currency(val) -> str:
    """Converts raw numeric values into formatted INR Crores or Lakhs."""
    try:
        num = float(val)
    except (ValueError, TypeError):
        return "N/A"

    if num >= 10_000_000:  # 1 Crore = 10,000,000 (10 Million)
        crores = num / 10_000_000
        return f"₹{crores:,.2f} Cr"
    elif num >= 100_000:   # 1 Lakh = 100,000
        lakhs = num / 100_000
        return f"₹{lakhs:,.2f} Lakh"
    else:
        return f"₹{num:,.2f}"

def normalize_stock_data(raw_data: dict, exchange: str = "NSE") -> dict:
    """Normalizes financial metrics to explicit INR units based on exchange."""
    normalized = raw_data.copy()
    
    raw_mcap = raw_data.get("market_cap")
    
    # Format Market Cap specifically for Indian Exchanges (NSE/BSE)
    if exchange in ["NSE", "BSE", "NSEI", "BOM"]:
        normalized["formatted_market_cap"] = format_indian_currency(raw_mcap)
        normalized["currency"] = "INR"
    else:
        # Fallback for foreign assets
        try:
            num = float(raw_mcap)
            normalized["formatted_market_cap"] = f"${num/1_000_000_000:,.2f} B"
            normalized["currency"] = "USD"
        except (ValueError, TypeError):
            normalized["formatted_market_cap"] = "N/A"
            normalized["currency"] = "Unknown"

    return normalized
