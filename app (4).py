"""
Analyseur de portefeuille — webapp Streamlit
Récupère les données réelles via Yahoo Finance (yfinance), calcule performance,
corrélation, volatilité, VaR et Expected Shortfall pour un portefeuille de tickers.

Lancer avec :   streamlit run app.py
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

from finance import full_portfolio_analysis
from currency import convert_prices
from tickers import POPULAR_TICKERS, get_company_name
from memory import load_last_portfolio, save_last_portfolio
from export import build_excel_report, build_pdf_report

st.set_page_config(page_title="Portfolio101", page_icon="favicon.png", layout="wide")
st.logo("logo_wordmark.svg", icon_image="favicon.png", size="large")

st.markdown("""
<style>
    .stMetric { background: white; border: 1px solid rgba(0,0,0,0.08); border-left: 3px solid #6B2FBF; border-radius: 12px; padding: 10px; }
    div[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)

st.image("logo_wordmark.svg", width=320)
st.caption("Performance historique · corrélation · volatilité · VaR · Expected Shortfall — données réelles via Yahoo Finance")

saved = load_last_portfolio()

# --------------------------------------------------------------- sidebar ---
with st.sidebar:
    st.header("Composition du portefeuille")

    tickers = st.multiselect(
        "Tickers",
        options=sorted(set(POPULAR_TICKERS) | set(saved.get("tickers", []))),
        default=saved.get("tickers", ["AAPL", "MSFT", "GOOGL"]),
        accept_new_options=True,
        help="Choisissez dans la liste ou tapez un symbole Yahoo Finance personnalisé puis validez avec Entrée "
             "(ex: MC.PA pour LVMH, CW8.PA pour un ETF MSCI World)."
    )

    st.subheader("Devise du portefeuille")
    currencies = ["EUR", "USD", "GBP", "CHF", "JPY", "CAD"]
    target_currency = st.selectbox(
        "Convertir tous les actifs en", currencies,
        index=currencies.index(saved.get("currency", "EUR")) if saved.get("currency") in currencies else 0,
        help="Chaque actif est automatiquement converti depuis sa devise native vers celle-ci, via les taux de change historiques."
    )

    st.subheader("Période")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Début", value=date.today() - timedelta(days=365 * 2))
    with col2:
        end_date = st.date_input("Fin", value=date.today())

    freq_label = st.selectbox("Fréquence des données", ["Quotidienne", "Hebdomadaire", "Mensuelle"], index=0,
                               help="La fréquence à laquelle les rendements sont mesurés. Influence l'annualisation des indicateurs.")
    freq = {"Quotidienne": "daily", "Hebdomadaire": "weekly", "Mensuelle": "monthly"}[freq_label]

    st.subheader("Pondérations")
    st.caption("Doit sommer à exactement 100% pour lancer l'analyse.")

    if st.button("⚖️ Répartir équitablement") and tickers:
        base = round(100 / len(tickers), 2)
        for t in tickers:
            st.session_state[f"w_{t}"] = base
        # corrige l'arrondi sur le dernier actif pour retomber exactement à 100%
        rounding_diff = round(100 - base * len(tickers), 2)
        st.session_state[f"w_{tickers[-1]}"] = round(base + rounding_diff, 2)
        st.rerun()

    weights_pct = {}
    saved_weights = saved.get("weights", {})
    for t in tickers:
        default_w = saved_weights.get(t, round(100 / len(tickers), 1)) if tickers else 0
        weights_pct[t] = st.slider(t, 0.0, 100.0, default_w, 0.5, key=f"w_{t}")

    total_w = sum(weights_pct.values()) if tickers else 0
    weights_ok = bool(tickers) and abs(total_w - 100) < 0.01
    if tickers:
        if weights_ok:
            st.success(f"Total des pondérations : {total_w:.1f}% ✓")
        else:
            st.error(f"Total des pondérations : {total_w:.1f}% — doit être exactement 100% pour lancer l'analyse.")

    st.subheader("Paramètres de risque")
    risk_free = st.number_input(
        "Taux sans risque annuel (%)", value=float(saved.get("risk_free", 3.0)), step=0.1,
        help="Rendement d'un placement considéré sans risque (ex: taux d'un livret ou d'une obligation d'État). "
             "Sert de référence pour calculer le ratio de Sharpe."
    ) / 100
    confidence = st.selectbox(
        "Niveau de confiance (VaR / ES)", [0.90, 0.95, 0.975, 0.99],
        index=[0.90, 0.95, 0.975, 0.99].index(saved.get("confidence", 0.95)) if saved.get("confidence") in [0.90, 0.95, 0.975, 0.99] else 1,
        format_func=lambda x: f"{int(x*100)}%",
        help="Le seuil de probabilité utilisé pour la VaR et l'Expected Shortfall. 95% = on regarde les 5% pires cas."
    )

    run = st.button("🔎 Analyser le portefeuille", type="primary", use_container_width=True,
                     disabled=not weights_ok)


# --------------------------------------------------------------- fetch -----
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_prices(tickers, start, end):
    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if len(tickers) == 1:
        prices = data[["Close"]].copy()
        prices.columns = tickers
    else:
        prices = data["Close"].copy()
    prices = prices.dropna(how="all").ffill().dropna()
    return prices


def resample_prices(prices: pd.DataFrame, freq: str) -> pd.DataFrame:
    if freq == "weekly":
        return prices.resample("W-FRI").last().dropna()
    if freq == "monthly":
        return prices.resample("ME").last().dropna()
    return prices


# ------------------------------------------------------------------ main ---
if not tickers:
    st.info("👈 Ajoutez au moins un ticker dans la barre latérale pour commencer.")
    st.stop()

with st.expander("Composition sélectionnée", expanded=False):
    for t in tickers:
        st.write(f"**{t}** — {get_company_name(t)} ({weights_pct.get(t, 0):.1f}%)")

if run:
    st.session_state["analyzed"] = True

if st.session_state.get("analyzed") and not weights_ok:
    st.warning("Ajustez les pondérations à exactement 100% dans la barre latérale pour relancer l'analyse.")
    st.stop()

if st.session_state.get("analyzed"):
    with st.spinner("Récupération des données Yahoo Finance…"):
        try:
            raw_prices = fetch_prices(tuple(tickers), start_date, end_date)
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            st.stop()

    missing = [t for t in tickers if t not in raw_prices.columns]
    if missing:
        st.warning(f"Ticker(s) introuvable(s) ou sans données sur cette période : {', '.join(missing)}")

    valid_tickers = [t for t in tickers if t in raw_prices.columns]
    if len(valid_tickers) < 2:
        st.error("Il faut au moins 2 tickers valides avec des données pour calculer la corrélation et les autres métriques.")
        st.stop()

    prices_native = raw_prices[valid_tickers]
    with st.spinner("Conversion des devises…"):
        prices_converted, currency_info = convert_prices(prices_native, target_currency, start_date, end_date)

    not_converted = [t for t, i in currency_info.items() if "introuvable" in i["status"]]
    if not_converted:
        st.warning(
            f"Taux de change introuvable pour : {', '.join(not_converted)} — "
            f"prix laissés dans leur devise native, ce qui fausse la comparaison."
        )
    with st.expander("Détail des conversions de devise"):
        for t, i in currency_info.items():
            st.write(f"**{t}** ({i['native']}) : {i['status']}")

    prices = resample_prices(prices_converted, freq)
    if len(prices) < 5:
        st.error("Pas assez de points de données sur la période/fréquence choisie. Élargissez la période.")
        st.stop()

    raw_weights_sum = sum(weights_pct[t] for t in valid_tickers) or 1
    weights = {t: weights_pct[t] / raw_weights_sum for t in valid_tickers}
    result = full_portfolio_analysis(prices, weights, freq, risk_free, confidence)

    save_last_portfolio({
        "tickers": valid_tickers, "weights": weights_pct, "currency": target_currency,
        "risk_free": risk_free * 100, "confidence": confidence,
    })

    # ---------------------------------------------------------- metrics ---
    st.subheader("Indicateurs de performance et de risque")
    metrics = [
        ("Rendement total", f"{result['total_return']*100:.1f}%",
         "Variation totale de la valeur du portefeuille entre le début et la fin de la période."),
        ("CAGR (annualisé)", f"{result['cagr']*100:.1f}%",
         "Taux de croissance annuel moyen composé : le rendement annuel constant qui aurait produit le même résultat final."),
        ("Volatilité annualisée", f"{result['volatility_annualized']*100:.1f}%",
         "Ampleur des variations du portefeuille dans le temps, ramenée à une base annuelle. Plus c'est élevé, plus le portefeuille est instable."),
        ("Ratio de Sharpe", f"{result['sharpe']:.2f}",
         "Rendement obtenu par unité de risque prise, au-delà du taux sans risque. Plus il est élevé, meilleur est le couple rendement/risque."),
        ("Max drawdown", f"{result['max_drawdown']*100:.1f}%",
         "La plus grosse perte subie entre un sommet et le creux suivant sur la période — le pire scénario réellement vécu."),
        (f"VaR historique ({int(confidence*100)}%)", f"{result['var_historical']*100:.2f}%",
         "Perte maximale attendue par période, avec le niveau de confiance choisi (calculée directement sur l'historique des rendements)."),
        (f"Expected Shortfall ({int(confidence*100)}%)", f"{result['es_historical']*100:.2f}%",
         "Perte moyenne dans les pires cas au-delà de la VaR — répond à \"si ça tourne mal, en moyenne je perds combien ?\"."),
        (f"VaR paramétrique ({int(confidence*100)}%)", f"{result['var_parametric']*100:.2f}%",
         "Même idée que la VaR historique, mais calculée en supposant que les rendements suivent une loi normale."),
    ]
    cols = st.columns(4)
    for i, (label, value, help_text) in enumerate(metrics):
        cols[i % 4].metric(label, value, help=help_text)

    st.divider()

    # ---------------------------------------------------------- chart -----
    st.subheader(f"Performance cumulée (base 100, en {target_currency})")
    norm_prices = prices / prices.iloc[0] * 100
    ASSET_COLORS = ["#111111", "#9B7FD1", "#C9A227", "#4A9B8E", "#B2703B", "#5B7B95"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result["portfolio_value"].index, y=result["portfolio_value"],
                              name="Portefeuille", line=dict(width=3, color="#6B2FBF")))
    for i, t in enumerate(valid_tickers):
        fig.add_trace(go.Scatter(x=norm_prices.index, y=norm_prices[t], name=t,
                                  line=dict(width=1.3, dash="dot", color=ASSET_COLORS[i % len(ASSET_COLORS)])))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------ correlation ---
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("Matrice de corrélation")
        st.caption("Corrélation des rendements entre chaque paire d'actifs (-1 à +1). Proche de 1 = évoluent ensemble, proche de -1 = évoluent en sens inverse, proche de 0 = pas de lien.")
        corr = result["correlation"]
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="PuOr", zmin=-1, zmax=1,
                              aspect="auto")
        fig_corr.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white")
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_right:
        st.subheader("Distribution des rendements")
        st.caption("Fréquence des rendements observés par période. La ligne pointillée marque le seuil de la VaR.")
        fig_hist = px.histogram(result["portfolio_returns"] * 100, nbins=40,
                                 labels={"value": "Rendement par période (%)"},
                                 color_discrete_sequence=["#6B2FBF"])
        fig_hist.add_vline(x=-result["var_historical"] * 100, line_color="#B23B3B", line_dash="dash",
                            annotation_text="VaR")
        fig_hist.update_layout(height=380, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.caption(
        f"Basé sur {result['n_periods']} périodes ({freq_label.lower()}) entre {start_date} et {end_date}, "
        f"tous les actifs convertis en {target_currency}. "
        "Portefeuille simulé en buy-and-hold (sans rééquilibrage). "
        "Performances passées, ne préjugent pas des performances futures. Ceci n'est pas un conseil en investissement."
    )

    # ---------------------------------------------------------- exports ---
    st.divider()
    st.subheader("Exporter les résultats")

    chart_data = norm_prices.copy()
    chart_data.insert(0, "Portefeuille", result["portfolio_value"])

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        excel_bytes = build_excel_report(result, target_currency, start_date, end_date, freq_label, chart_data)
        st.download_button("📊 Télécharger en Excel", data=excel_bytes,
                            file_name="portefeuille_analyse.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)

    with exp_col2:
        perf_png = fig.to_image(format="png", width=1000, height=500, scale=2)
        st.download_button("🖼️ Télécharger le graphique (PNG)", data=perf_png,
                            file_name="performance_portefeuille.png", mime="image/png",
                            use_container_width=True)

    with exp_col3:
        corr_png = fig_corr.to_image(format="png", width=700, height=600, scale=2)
        pdf_bytes = build_pdf_report(result, target_currency, start_date, end_date, freq_label,
                                      valid_tickers, perf_png, corr_png)
        st.download_button("📄 Télécharger le rapport PDF", data=pdf_bytes,
                            file_name="rapport_portefeuille.pdf", mime="application/pdf",
                            use_container_width=True)
