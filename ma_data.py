"""
Récupération des données financières (Yahoo Finance) pour la valorisation M&A :
fondamentaux d'une société cible ou d'un comparable, avec repli propre si une
donnée est indisponible (l'utilisateur peut toujours la saisir manuellement).
"""
import yfinance as yf
import streamlit as st


def _find_row(df, candidates: list):
    """Cherche la première ligne correspondant à l'un des libellés candidats dans un état financier yfinance."""
    if df is None or df.empty:
        return None
    for label in candidates:
        for idx in df.index:
            if label.lower() == str(idx).lower():
                return df.loc[idx]
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_company_fundamentals(ticker: str) -> dict:
    """
    Fondamentaux d'une société pour la valorisation : prix, capitalisation, dette nette,
    EBITDA, chiffre d'affaires, bêta, etc. Toute valeur indisponible est laissée à None
    (à saisir manuellement dans l'interface).
    """
    t = yf.Ticker(ticker)
    try:
        info = t.info or {}
    except Exception:
        info = {}

    market_cap = info.get("marketCap")
    total_debt = info.get("totalDebt") or 0
    total_cash = info.get("totalCash") or 0
    net_debt = (total_debt or 0) - (total_cash or 0)
    ev = info.get("enterpriseValue")
    if ev is None and market_cap is not None:
        ev = market_cap + net_debt

    fundamentals = {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName") or ticker,
        "currency": info.get("currency", "USD"),
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "market_cap": market_cap,
        "net_debt": net_debt,
        "enterprise_value": ev,
        "revenue": info.get("totalRevenue"),
        "ebitda": info.get("ebitda"),
        "net_income": info.get("netIncomeToCommon"),
        "beta": info.get("beta") or 1.0,
        "week52_low": info.get("fiftyTwoWeekLow"),
        "week52_high": info.get("fiftyTwoWeekHigh"),
    }

    # historique (meilleur effort) pour proposer des hypothèses de croissance/marge par défaut
    try:
        fin = t.financials
        revenue_row = _find_row(fin, ["Total Revenue"])
        ebitda_row = _find_row(fin, ["EBITDA", "Normalized EBITDA"])
        if revenue_row is not None and len(revenue_row.dropna()) >= 2:
            values = revenue_row.dropna().sort_index()
            years = len(values) - 1
            if years > 0 and values.iloc[0] > 0:
                cagr = (values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1
                fundamentals["historical_revenue_cagr"] = float(cagr)
        if ebitda_row is not None and revenue_row is not None:
            common_dates = ebitda_row.dropna().index.intersection(revenue_row.dropna().index)
            if len(common_dates) > 0:
                margins = (ebitda_row[common_dates] / revenue_row[common_dates]).dropna()
                if len(margins) > 0:
                    fundamentals["historical_ebitda_margin"] = float(margins.mean())
    except Exception:
        pass

    return fundamentals


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_peer_multiples(ticker: str) -> dict:
    """Multiples de valorisation observés pour un comparable boursier (EV/EBITDA, EV/Revenue, P/E)."""
    f = fetch_company_fundamentals(ticker)
    result = {"ticker": ticker, "name": f["name"]}

    if f["enterprise_value"] and f["ebitda"] and f["ebitda"] > 0:
        result["ev_ebitda"] = f["enterprise_value"] / f["ebitda"]
    else:
        result["ev_ebitda"] = None

    if f["enterprise_value"] and f["revenue"] and f["revenue"] > 0:
        result["ev_revenue"] = f["enterprise_value"] / f["revenue"]
    else:
        result["ev_revenue"] = None

    if f["market_cap"] and f["net_income"] and f["net_income"] > 0:
        result["pe"] = f["market_cap"] / f["net_income"]
    else:
        result["pe"] = None

    return result
