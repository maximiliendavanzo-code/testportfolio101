"""
Portfolio101 — webapp Streamlit
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
from inflation import deflate_prices_with_real_cpi
from currency import convert_prices
from tickers import POPULAR_TICKERS, get_company_name
from memory import load_last_portfolio, save_last_portfolio
from export import build_excel_report, build_pdf_report
from i18n import t, render_language_selector

st.set_page_config(page_title="Portfolio101", page_icon="favicon.png", layout="wide")
st.logo("logo_wordmark.svg", icon_image="favicon.png", size="large")

st.markdown("""
<style>
    .stMetric { background: white; border: 1px solid rgba(0,0,0,0.08); border-left: 3px solid #6B2FBF; border-radius: 12px; padding: 10px; }
    div[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; }
    .feature-card { background: white; border: 1px solid rgba(0,0,0,0.08); border-radius: 14px; padding: 20px; height: 100%; }
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("page", "home")

# --------------------------------------------------------- top bar (toutes pages) ---
render_language_selector()


# ================================================================= HOME ===
def render_home_page():
    st.image("logo_wordmark.svg", width=380)
    st.subheader(t("home_subtitle"))
    st.write(t("home_description"))
    st.write("")

    c1, c2, c3 = st.columns(3)
    for col, num in zip([c1, c2, c3], [1, 2, 3]):
        with col:
            st.markdown(
                f'<div class="feature-card"><b>{t(f"home_feature_{num}_title")}</b>'
                f'<p style="color:#5B5F6B;margin-top:6px">{t(f"home_feature_{num}_text")}</p></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    if st.button(t("home_cta"), type="primary"):
        st.session_state["page"] = "app"
        st.rerun()


# ================================================================== APP ===
def render_app_page():
    st.image("logo_wordmark.svg", width=280)
    st.caption(t("tagline"))

    saved = load_last_portfolio()

    with st.sidebar:
        if st.button(t("back_home")):
            st.session_state["page"] = "home"
            st.rerun()
        st.divider()

        st.header(t("sidebar_header"))

        tickers = st.multiselect(
            t("tickers_label"),
            options=sorted(set(POPULAR_TICKERS) | set(saved.get("tickers", []))),
            default=saved.get("tickers", ["AAPL", "MSFT", "GOOGL"]),
            accept_new_options=True,
            help=t("tickers_help"),
        )

        st.subheader(t("currency_subheader"))
        currencies = ["EUR", "USD", "GBP", "CHF", "JPY", "CAD"]
        target_currency = st.selectbox(
            t("currency_label"), currencies,
            index=currencies.index(saved.get("currency", "EUR")) if saved.get("currency") in currencies else 0,
            help=t("currency_help"),
        )

        st.subheader(t("period_subheader"))
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(t("start_label"), value=date.today() - timedelta(days=365 * 2))
        with col2:
            end_date = st.date_input(t("end_label"), value=date.today())

        freq_options = ["daily", "weekly", "monthly"]
        freq_display = {"daily": t("freq_daily"), "weekly": t("freq_weekly"), "monthly": t("freq_monthly")}
        freq = st.selectbox(t("freq_label"), freq_options, index=0,
                             format_func=lambda k: freq_display[k], help=t("freq_help"))

        st.subheader(t("weights_subheader"))
        st.caption(t("weights_caption"))

        if st.button(t("equal_weight_button")) and tickers:
            base = round(100 / len(tickers), 2)
            for tk in tickers:
                st.session_state[f"w_{tk}"] = base
            rounding_diff = round(100 - base * len(tickers), 2)
            st.session_state[f"w_{tickers[-1]}"] = round(base + rounding_diff, 2)
            st.rerun()

        weights_pct = {}
        saved_weights = saved.get("weights", {})
        for tk in tickers:
            default_w = saved_weights.get(tk, round(100 / len(tickers), 1)) if tickers else 0
            weights_pct[tk] = st.slider(tk, 0.0, 100.0, default_w, 0.5, key=f"w_{tk}")

        total_w = sum(weights_pct.values()) if tickers else 0
        weights_ok = bool(tickers) and abs(total_w - 100) < 0.01
        if tickers:
            if weights_ok:
                st.success(t("weights_ok", total=total_w))
            else:
                st.error(t("weights_error", total=total_w))

        st.subheader(t("risk_subheader"))
        risk_free = st.number_input(
            t("riskfree_label"), value=float(saved.get("risk_free", 3.0)), step=0.1, help=t("riskfree_help")
        ) / 100
        confidence_options = [0.90, 0.95, 0.975, 0.99]
        confidence = st.selectbox(
            t("confidence_label"), confidence_options,
            index=confidence_options.index(saved.get("confidence", 0.95)) if saved.get("confidence") in confidence_options else 1,
            format_func=lambda x: f"{int(x*100)}%", help=t("confidence_help"),
        )

        st.subheader(t("inflation_subheader"))
        adjust_inflation = st.checkbox(t("inflation_toggle"), value=bool(saved.get("adjust_inflation", False)),
                                        help=t("inflation_help"))

        run = st.button(t("analyze_button"), type="primary", use_container_width=True, disabled=not weights_ok)

    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_prices(tks, start, end):
        data = yf.download(tks, start=start, end=end, auto_adjust=True, progress=False)
        if len(tks) == 1:
            prices = data[["Close"]].copy()
            prices.columns = tks
        else:
            prices = data["Close"].copy()
        return prices.dropna(how="all").ffill().dropna()

    def resample_prices(prices: pd.DataFrame, freq_code: str) -> pd.DataFrame:
        if freq_code == "weekly":
            return prices.resample("W-FRI").last().dropna()
        if freq_code == "monthly":
            return prices.resample("ME").last().dropna()
        return prices

    if not tickers:
        st.info(t("no_ticker_info"))
        st.stop()

    with st.expander(t("composition_expander"), expanded=False):
        for tk in tickers:
            st.write(f"**{tk}** — {get_company_name(tk)} ({weights_pct.get(tk, 0):.1f}%)")

    if run:
        st.session_state["analyzed"] = True

    if st.session_state.get("analyzed") and not weights_ok:
        st.warning(t("weights_warning_relaunch"))
        st.stop()

    if not st.session_state.get("analyzed"):
        return

    with st.spinner(t("fetching_spinner")):
        try:
            raw_prices = fetch_prices(tuple(tickers), start_date, end_date)
        except Exception as e:
            st.error(t("fetch_error", e=e))
            st.stop()

    missing = [tk for tk in tickers if tk not in raw_prices.columns]
    if missing:
        st.warning(t("missing_tickers_warning", tickers=", ".join(missing)))

    valid_tickers = [tk for tk in tickers if tk in raw_prices.columns]
    if len(valid_tickers) < 2:
        st.error(t("min_2_tickers_error"))
        st.stop()

    prices_native = raw_prices[valid_tickers]
    with st.spinner(t("converting_spinner")):
        prices_converted, currency_info = convert_prices(prices_native, target_currency, start_date, end_date)

    not_converted = [tk for tk, i in currency_info.items() if "introuvable" in i["status"]]
    if not_converted:
        st.warning(t("fx_not_found_warning", tickers=", ".join(not_converted)))
    with st.expander(t("currency_details_expander")):
        for tk, i in currency_info.items():
            st.write(f"**{tk}** ({i['native']}) : {i['status']}")

    prices = resample_prices(prices_converted, freq)
    if len(prices) < 5:
        st.error(t("not_enough_data_error"))
        st.stop()

    inflation_info = None
    if adjust_inflation:
        with st.spinner(t("inflation_spinner")):
            real_prices, inflation_info = deflate_prices_with_real_cpi(prices, target_currency, start_date, end_date)
        if inflation_info["status"] == "ok":
            prices = real_prices
        else:
            st.warning(t("inflation_unavailable_warning", ccy=target_currency))
            adjust_inflation = False

    raw_weights_sum = sum(weights_pct[tk] for tk in valid_tickers) or 1
    weights = {tk: weights_pct[tk] / raw_weights_sum for tk in valid_tickers}
    result = full_portfolio_analysis(prices, weights, freq, risk_free, confidence)

    save_last_portfolio({
        "tickers": valid_tickers, "weights": weights_pct, "currency": target_currency,
        "risk_free": risk_free * 100, "confidence": confidence, "adjust_inflation": adjust_inflation,
    })

    # ---------------------------------------------------------- metrics ---
    st.subheader(t("metrics_subheader"))
    if adjust_inflation and inflation_info:
        st.info(t("real_terms_note", rate=inflation_info["annualized_rate"] * 100, ccy=target_currency))
    else:
        st.caption(t("nominal_terms_note"))
    conf_pct = int(confidence * 100)
    metrics = [
        (t("metric_total_return"), f"{result['total_return']*100:.1f}%", t("metric_total_return_help")),
        (t("metric_cagr"), f"{result['cagr']*100:.1f}%", t("metric_cagr_help")),
        (t("metric_vol"), f"{result['volatility_annualized']*100:.1f}%", t("metric_vol_help")),
        (t("metric_sharpe"), f"{result['sharpe']:.2f}", t("metric_sharpe_help")),
        (t("metric_mdd"), f"{result['max_drawdown']*100:.1f}%", t("metric_mdd_help")),
        (t("metric_var_hist", conf=conf_pct), f"{result['var_historical']*100:.2f}%", t("metric_var_hist_help")),
        (t("metric_es", conf=conf_pct), f"{result['es_historical']*100:.2f}%", t("metric_es_help")),
        (t("metric_var_param", conf=conf_pct), f"{result['var_parametric']*100:.2f}%", t("metric_var_param_help")),
    ]
    cols = st.columns(4)
    for i, (label, value, help_text) in enumerate(metrics):
        cols[i % 4].metric(label, value, help=help_text)

    st.divider()

    # ---------------------------------------------------------- chart -----
    st.subheader(t("performance_subheader", ccy=target_currency))
    norm_prices = prices / prices.iloc[0] * 100
    ASSET_COLORS = ["#111111", "#9B7FD1", "#C9A227", "#4A9B8E", "#B2703B", "#5B7B95"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result["portfolio_value"].index, y=result["portfolio_value"],
                              name=t("portfolio_label"), line=dict(width=3, color="#6B2FBF")))
    for i, tk in enumerate(valid_tickers):
        fig.add_trace(go.Scatter(x=norm_prices.index, y=norm_prices[tk], name=tk,
                                  line=dict(width=1.3, dash="dot", color=ASSET_COLORS[i % len(ASSET_COLORS)])))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(0,0,0,0.2)")
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white",
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------ correlation ---
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader(t("correlation_subheader"))
        st.caption(t("correlation_caption"))
        corr = result["correlation"]
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="PuOr", zmin=-1, zmax=1, aspect="auto")
        fig_corr.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white")
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_right:
        st.subheader(t("distribution_subheader"))
        st.caption(t("distribution_caption"))
        fig_hist = px.histogram(result["portfolio_returns"] * 100, nbins=40,
                                 labels={"value": "%"}, color_discrete_sequence=["#6B2FBF"])
        fig_hist.add_vline(x=-result["var_historical"] * 100, line_color="#B23B3B", line_dash="dash",
                            annotation_text="VaR")
        fig_hist.update_layout(height=380, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.caption(t("footer_caption", n=result["n_periods"], freq=freq_display[freq].lower(),
                  start=start_date, end=end_date, ccy=target_currency))

    # ---------------------------------------------------------- exports ---
    st.divider()
    st.subheader(t("export_subheader"))

    chart_data = norm_prices.copy()
    chart_data.insert(0, t("portfolio_label"), result["portfolio_value"])

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        excel_bytes = build_excel_report(result, target_currency, start_date, end_date, freq_display[freq], chart_data)
        st.download_button(t("export_excel"), data=excel_bytes, file_name="portefeuille_analyse.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)

    with exp_col2:
        perf_png = fig.to_image(format="png", width=1000, height=500, scale=2)
        st.download_button(t("export_png"), data=perf_png, file_name="performance_portefeuille.png",
                            mime="image/png", use_container_width=True)

    with exp_col3:
        corr_png = fig_corr.to_image(format="png", width=700, height=600, scale=2)
        pdf_bytes = build_pdf_report(result, target_currency, start_date, end_date, freq_display[freq],
                                      valid_tickers, perf_png, corr_png)
        st.download_button(t("export_pdf"), data=pdf_bytes, file_name="rapport_portefeuille.pdf",
                            mime="application/pdf", use_container_width=True)


# ================================================================ ROUTE ===
if st.session_state["page"] == "home":
    render_home_page()
else:
    render_app_page()
