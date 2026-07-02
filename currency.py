"""
Conversion des prix d'actifs vers une devise cible commune, via les taux
de change historiques récupérés sur Yahoo Finance.
"""
import pandas as pd
import yfinance as yf
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def get_ticker_currency(ticker: str) -> str:
    """Devise native d'un ticker (ex: 'USD', 'EUR'). 'USD' par défaut si indisponible."""
    try:
        return yf.Ticker(ticker).fast_info["currency"] or "USD"
    except Exception:
        return "USD"


@st.cache_data(ttl=3600, show_spinner=False)
def get_fx_rate_series(from_ccy: str, to_ccy: str, start, end) -> pd.Series | None:
    """Série de taux de change from_ccy -> to_ccy (1 from_ccy = X to_ccy) sur la période."""
    if from_ccy == to_ccy:
        return None

    def _download_close(pair):
        data = yf.download(pair, start=start, end=end, auto_adjust=True, progress=False)
        if data.empty:
            return None
        close = data["Close"]
        return close.iloc[:, 0] if hasattr(close, "columns") else close

    direct = _download_close(f"{from_ccy}{to_ccy}=X")
    if direct is not None:
        return direct

    inverse = _download_close(f"{to_ccy}{from_ccy}=X")
    if inverse is not None:
        return 1 / inverse

    return None


def convert_prices(prices: pd.DataFrame, target_currency: str, start, end) -> tuple[pd.DataFrame, dict]:
    """
    Convertit chaque colonne (ticker) de `prices` vers target_currency.
    Retourne (prix convertis, infos par ticker: devise native + statut de conversion).
    """
    converted = prices.copy()
    info = {}
    for ticker in prices.columns:
        native = get_ticker_currency(ticker)
        if native == target_currency:
            info[ticker] = {"native": native, "status": "déjà dans la devise cible"}
            continue
        fx = get_fx_rate_series(native, target_currency, start, end)
        if fx is None:
            info[ticker] = {"native": native, "status": "taux introuvable — prix laissé en devise native"}
            continue
        fx = fx.reindex(converted.index).ffill().bfill()
        converted[ticker] = converted[ticker] * fx
        info[ticker] = {"native": native, "status": f"converti ({native} → {target_currency})"}
    return converted, info
