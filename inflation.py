"""
Récupération de l'inflation réelle (indice des prix à la consommation, CPI/HICP)
par devise, depuis FRED (Federal Reserve Economic Data) — source publique,
sans clé d'API nécessaire pour le téléchargement CSV.
"""
import pandas as pd
import streamlit as st

# Séries CPI/HICP mensuelles officielles (OCDE / Eurostat / BLS, relayées par FRED)
CPI_SERIES = {
    "USD": "CPIAUCSL",            # Etats-Unis (BLS)
    "EUR": "CP0000EZ19M086NEST",  # Zone euro, HICP (Eurostat)
    "GBP": "GBRCPIALLMINMEI",     # Royaume-Uni (OCDE)
    "CHF": "CHECPIALLMINMEI",     # Suisse (OCDE)
    "JPY": "JPNCPIALLMINMEI",     # Japon (OCDE)
    "CAD": "CANCPIALLMINMEI",     # Canada (OCDE)
}

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}&coed={end}"


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_cpi_series(currency: str, start, end):
    """Récupère la série mensuelle de l'indice des prix pour une devise, sur la période demandée."""
    series_id = CPI_SERIES.get(currency)
    if not series_id:
        return None
    url = FRED_CSV_URL.format(series_id=series_id, start=start, end=end)
    try:
        df = pd.read_csv(url)
    except Exception:
        return None
    if df.shape[1] < 2:
        return None
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    if df.empty:
        return None
    return df.set_index("date")["value"].sort_index()


def deflate_prices_with_real_cpi(prices: pd.DataFrame, currency: str, start, end):
    """
    Convertit des prix nominaux en prix réels, en utilisant l'inflation réellement
    constatée (mois par mois) sur la devise et la période du portefeuille — pas un
    taux supposé constant.

    Retourne (prix réels ou None si indisponible, infos: statut + taux annualisé observé).
    """
    cpi = fetch_cpi_series(currency, start, end)
    if cpi is None or len(cpi) < 2:
        return None, {"status": "unavailable"}

    # aligne l'indice CPI (mensuel) sur les dates exactes du portefeuille, par interpolation temporelle
    combined_index = cpi.index.union(prices.index)
    cpi_aligned = cpi.reindex(combined_index).sort_index().interpolate(method="time").reindex(prices.index)
    cpi_aligned = cpi_aligned.ffill().bfill()

    if cpi_aligned.isna().any():
        return None, {"status": "unavailable"}

    deflator = cpi_aligned / cpi_aligned.iloc[0]
    real_prices = prices.div(deflator, axis=0)

    n_years = (prices.index[-1] - prices.index[0]).days / 365.25
    total_inflation = cpi_aligned.iloc[-1] / cpi_aligned.iloc[0] - 1
    annualized_rate = (1 + total_inflation) ** (1 / n_years) - 1 if n_years > 0.05 else total_inflation

    return real_prices, {
        "status": "ok",
        "annualized_rate": annualized_rate,
        "total_inflation": total_inflation,
        "series_id": CPI_SERIES[currency],
    }
