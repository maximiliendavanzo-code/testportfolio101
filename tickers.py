"""
Aide à la sélection de tickers : liste de valeurs populaires pour un
démarrage rapide, et résolution du nom complet d'une société.
"""
import streamlit as st
import yfinance as yf

POPULAR_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",   # tech US
    "JPM", "KO", "DIS",                                        # autres US
    "MC.PA", "OR.PA", "SAN.PA", "TTE.PA", "AI.PA", "BNP.PA",   # CAC 40
    "CW8.PA", "SPY", "VOO", "EEM",                             # ETF
    "BTC-USD", "ETH-USD",                                      # crypto
]


@st.cache_data(ttl=86400, show_spinner=False)
def get_company_name(ticker: str) -> str:
    """Nom complet d'une société/actif à partir de son ticker. Retourne le ticker si indisponible."""
    try:
        info = yf.Ticker(ticker).info
        return info.get("shortName") or info.get("longName") or ticker
    except Exception:
        return ticker
