"""
Finance101 — webapp Streamlit
Portail avec 3 outils : Portfolio101 (analyse de portefeuille, fonctionnel),
CIB101 et M&A101 (à venir). Portfolio101 récupère les données réelles via
Yahoo Finance et calcule performance, corrélation, volatilité, VaR et
Expected Shortfall pour un portefeuille de tickers.

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
from ma_data import fetch_company_fundamentals, fetch_peer_multiples
from ma_valuation import compute_wacc, compute_dcf, dcf_sensitivity, implied_valuation_from_multiples, compute_synergies_npv

st.set_page_config(page_title="Finance101", page_icon="favicon.png", layout="wide")
st.logo("logo_finance101.svg", icon_image="favicon.png", size="large")

st.markdown("""
<style>
    .stMetric { background: white; border: 1px solid rgba(0,0,0,0.08); border-left: 3px solid #6B2FBF; border-radius: 12px; padding: 10px; }
    div[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; }
    .feature-card { background: white; border: 1px solid rgba(0,0,0,0.08); border-radius: 14px; padding: 20px; height: 100%; }
    .tool-card { background: white; border: 1px solid rgba(0,0,0,0.08); border-radius: 16px; padding: 24px; height: 100%; }
    .tool-badge { display: inline-block; background: #F0EFEA; color: #5B5F6B; font-size: 11px; padding: 3px 9px; border-radius: 999px; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("page", "finance_home")

# --------------------------------------------------------- top bar (toutes pages) ---
render_language_selector()


# ============================================================ FINANCE101 ===
def render_finance_home():
    st.image("logo_finance101.svg", width=340)
    st.subheader(t("finance_home_subtitle"))
    st.write(t("finance_home_description"))
    st.write("")

    tools = [
        ("logo_wordmark.svg", "portfolio", "tool_portfolio_desc", True),
        ("logo_cib101.svg", "cib", "tool_cib_desc", False),
        ("logo_ma101.svg", "ma", "tool_ma_desc", False),
    ]
    cols = st.columns(3)
    for col, (logo, page_key, desc_key, available) in zip(cols, tools):
        with col:
            st.markdown('<div class="tool-card">', unsafe_allow_html=True)
            st.image(logo, width=180)
            st.write(t(desc_key))
            if not available:
                st.markdown(f'<span class="tool-badge">{t("coming_soon_badge")}</span>', unsafe_allow_html=True)
            st.write("")
            if st.button(t("open_button"), key=f"open_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


def render_coming_soon(logo_file: str, back_label_key: str = "back_to_finance"):
    if st.button(t(back_label_key)):
        st.session_state["page"] = "finance_home"
        st.rerun()
    st.write("")
    st.image(logo_file, width=280)
    st.info(t("coming_soon_text"))


# ================================================================== M&A ===
def render_ma_page():
    import numpy as np

    if st.button(t("back_to_finance")):
        st.session_state["page"] = "finance_home"
        st.rerun()
    st.image("logo_ma101.svg", width=220)
    st.caption(t("ma_tagline"))

    # ------------------------------------------------------- cible -----
    st.subheader(t("ma_target_subheader"))
    mode = st.radio(t("ma_target_mode"), [t("ma_target_ticker"), t("ma_target_manual")], horizontal=True)
    use_ticker = mode == t("ma_target_ticker")

    fundamentals = {}
    if use_ticker:
        ticker = st.text_input(t("ma_ticker_label"), value="AAPL", help=t("ma_ticker_help"))
        if ticker:
            with st.spinner(t("fetching_spinner")):
                fundamentals = fetch_company_fundamentals(ticker.strip().upper())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input(t("ma_name_label"), value=fundamentals.get("name", ""))
        revenue = st.number_input(t("ma_revenue_label"), value=float(fundamentals.get("revenue") or 1_000_000_000) / 1_000_000, step=10.0, help=t("ma_units_help"))
    with col2:
        ebitda = st.number_input(t("ma_ebitda_label"), value=float(fundamentals.get("ebitda") or (fundamentals.get("revenue") or 1_000_000_000) * 0.2) / 1_000_000, step=10.0)
        net_debt = st.number_input(t("ma_netdebt_label"), value=float(fundamentals.get("net_debt") or 0.0) / 1_000_000, step=10.0)
    with col3:
        shares_outstanding = st.number_input(t("ma_shares_label"), value=float(fundamentals.get("shares_outstanding") or 100_000_000) / 1_000_000, step=1.0, help=t("ma_shares_help"))
        current_price = st.number_input(t("ma_price_label"), value=float(fundamentals.get("price") or 0.0), step=1.0)
    with col4:
        beta = st.number_input(t("ma_beta_label"), value=float(fundamentals.get("beta") or 1.0), step=0.05)
        market_cap = st.number_input(t("ma_marketcap_label"), value=float(fundamentals.get("market_cap") or current_price * shares_outstanding * 1_000_000 or 1_000_000_000) / 1_000_000, step=10.0, help=t("ma_units_help"))

    st.divider()

    tab_dcf, tab_comps, tab_trans, tab_syn, tab_ff = st.tabs([
        t("ma_tab_dcf"), t("ma_tab_comps"), t("ma_tab_trans"), t("ma_tab_syn"), t("ma_tab_ff"),
    ])

    valuation_ranges = {}  # alimenté par chaque onglet, utilisé par le football field

    # ============================================================= DCF ===
    with tab_dcf:
        st.markdown(f"**{t('ma_dcf_assumptions')}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            risk_free_rate = st.number_input(t("ma_riskfree"), value=3.0, step=0.1) / 100
            equity_risk_premium = st.number_input(t("ma_erp"), value=5.0, step=0.1) / 100
            cost_of_debt = st.number_input(t("ma_costdebt"), value=5.0, step=0.1) / 100
        with c2:
            tax_rate = st.number_input(t("ma_taxrate"), value=25.0, step=0.5) / 100
            default_growth = (fundamentals.get("historical_revenue_cagr") or 0.05) * 100
            revenue_growth = st.number_input(t("ma_revgrowth"), value=round(default_growth, 1), step=0.5) / 100
            default_margin = (fundamentals.get("historical_ebitda_margin") or 0.20) * 100
            ebitda_margin = st.number_input(t("ma_ebitdamargin"), value=round(default_margin, 1), step=0.5) / 100
        with c3:
            da_pct = st.number_input(t("ma_dapct"), value=5.0, step=0.5) / 100
            capex_pct = st.number_input(t("ma_capexpct"), value=5.0, step=0.5) / 100
            nwc_pct = st.number_input(t("ma_nwcpct"), value=10.0, step=0.5) / 100

        c4, c5 = st.columns(2)
        with c4:
            terminal_method_label = st.radio(t("ma_terminal_method"), [t("ma_terminal_growth"), t("ma_terminal_exit")], horizontal=True)
            terminal_method = "growth" if terminal_method_label == t("ma_terminal_growth") else "exit_multiple"
        with c5:
            if terminal_method == "growth":
                terminal_growth = st.number_input(t("ma_terminal_growth_rate"), value=2.0, step=0.1) / 100
                exit_multiple = 8.0
            else:
                exit_multiple = st.number_input(t("ma_exit_multiple"), value=8.0, step=0.5)
                terminal_growth = 0.02

        wacc_info = compute_wacc(risk_free_rate, beta, equity_risk_premium, cost_of_debt, tax_rate, market_cap, net_debt)
        st.info(t("ma_wacc_result", wacc=wacc_info["wacc"] * 100, coe=wacc_info["cost_of_equity"] * 100))

        try:
            dcf_result = compute_dcf(
                revenue, [revenue_growth] * 5, ebitda_margin, da_pct, capex_pct, nwc_pct, tax_rate,
                wacc_info["wacc"], terminal_method, terminal_growth, exit_multiple, net_debt, shares_outstanding,
            )
            cols = st.columns(3)
            cols[0].metric(t("ma_ev_result"), f"{dcf_result['enterprise_value']:,.0f}")
            cols[1].metric(t("ma_equity_result"), f"{dcf_result['equity_value']:,.0f}")
            cols[2].metric(t("ma_pershare_result"), f"{dcf_result['value_per_share']:,.2f}")

            if current_price:
                upside = dcf_result["value_per_share"] / current_price - 1
                st.caption(t("ma_upside", upside=upside * 100))

            df_fcf = pd.DataFrame(dcf_result["rows"]).set_index("year")
            st.dataframe(df_fcf.style.format("{:,.1f}"), use_container_width=True)

            st.markdown(f"**{t('ma_sensitivity_title')}**")
            wacc_range = [wacc_info["wacc"] + d for d in [-0.02, -0.01, 0, 0.01, 0.02]]
            growth_range = [terminal_growth + d for d in [-0.01, -0.005, 0, 0.005, 0.01]]
            sens = dcf_sensitivity(revenue, [revenue_growth] * 5, ebitda_margin, da_pct, capex_pct, nwc_pct,
                                    tax_rate, wacc_range, growth_range, net_debt, shares_outstanding)
            sens.index = [f"{w*100:.1f}%" for w in wacc_range]
            sens.columns = [f"{g*100:.1f}%" for g in growth_range]
            st.dataframe(sens.style.format("{:,.1f}").background_gradient(cmap="PuOr", axis=None), use_container_width=True)

            valid_vals = sens.values[~np.isnan(sens.values.astype(float))]
            if len(valid_vals) > 0:
                valuation_ranges["DCF"] = (float(np.min(valid_vals)), dcf_result["value_per_share"], float(np.max(valid_vals)))
        except ValueError as e:
            st.error(str(e))

    # =========================================================== COMPS ===
    with tab_comps:
        peer_tickers = st.multiselect(t("ma_peers_label"), options=POPULAR_TICKERS,
                                       default=["MSFT", "GOOGL", "META"], help=t("ma_peers_help"))
        if peer_tickers:
            with st.spinner(t("fetching_spinner")):
                peer_data = [fetch_peer_multiples(p) for p in peer_tickers]
            df_peers = pd.DataFrame(peer_data).set_index("ticker")
            st.dataframe(df_peers.style.format({"ev_ebitda": "{:.1f}x", "ev_revenue": "{:.1f}x", "pe": "{:.1f}x"}),
                         use_container_width=True)

            ev_ebitda_multiples = [p["ev_ebitda"] for p in peer_data if p["ev_ebitda"]]
            if len(ev_ebitda_multiples) >= 2 and ebitda:
                comps_result = implied_valuation_from_multiples(ev_ebitda_multiples, ebitda, net_debt, shares_outstanding)
                cols = st.columns(3)
                cols[0].metric(t("ma_range_low"), f"{comps_result['valuation']['low']['per_share']:,.2f}")
                cols[1].metric(t("ma_range_median"), f"{comps_result['valuation']['median']['per_share']:,.2f}")
                cols[2].metric(t("ma_range_high"), f"{comps_result['valuation']['high']['per_share']:,.2f}")
                valuation_ranges["Comps"] = (comps_result["valuation"]["low"]["per_share"],
                                              comps_result["valuation"]["median"]["per_share"],
                                              comps_result["valuation"]["high"]["per_share"])
            else:
                st.warning(t("ma_not_enough_peers"))

    # ====================================================== TRANSACTIONS ===
    with tab_trans:
        st.caption(t("ma_trans_help"))
        default_trans = pd.DataFrame({
            t("ma_trans_deal"): ["Deal A", "Deal B", "Deal C"],
            "EV/EBITDA": [9.0, 10.5, 8.2],
        })
        edited = st.data_editor(default_trans, num_rows="dynamic", use_container_width=True, key="ma_trans_editor")
        trans_multiples = edited["EV/EBITDA"].dropna().tolist()
        trans_multiples = [m for m in trans_multiples if isinstance(m, (int, float)) and m > 0]
        if len(trans_multiples) >= 2 and ebitda:
            trans_result = implied_valuation_from_multiples(trans_multiples, ebitda, net_debt, shares_outstanding)
            cols = st.columns(3)
            cols[0].metric(t("ma_range_low"), f"{trans_result['valuation']['low']['per_share']:,.2f}")
            cols[1].metric(t("ma_range_median"), f"{trans_result['valuation']['median']['per_share']:,.2f}")
            cols[2].metric(t("ma_range_high"), f"{trans_result['valuation']['high']['per_share']:,.2f}")
            valuation_ranges["Transactions"] = (trans_result["valuation"]["low"]["per_share"],
                                                 trans_result["valuation"]["median"]["per_share"],
                                                 trans_result["valuation"]["high"]["per_share"])
        else:
            st.warning(t("ma_not_enough_trans"))

    # ========================================================= SYNERGIES ===
    with tab_syn:
        c1, c2 = st.columns(2)
        with c1:
            annual_synergies = st.number_input(t("ma_syn_amount"), value=50.0, step=5.0)
            syn_tax_rate = st.number_input(t("ma_taxrate"), value=25.0, step=0.5, key="syn_tax") / 100
        with c2:
            syn_discount_rate = st.number_input(t("ma_syn_discount"), value=10.0, step=0.5) / 100
            phase_years = st.slider(t("ma_syn_phasein_years"), 1, 5, 3)

        phase_in = [round((i + 1) / phase_years, 2) for i in range(phase_years)]
        st.caption(t("ma_syn_phasein_display", pct=", ".join(f"{p*100:.0f}%" for p in phase_in)))

        syn_result = compute_synergies_npv(annual_synergies, phase_in, syn_tax_rate, syn_discount_rate)
        cols = st.columns(2)
        cols[0].metric(t("ma_syn_npv"), f"{syn_result['npv']:,.0f}")
        if shares_outstanding:
            cols[1].metric(t("ma_syn_pershare"), f"{syn_result['npv']/shares_outstanding:,.2f}")
        st.dataframe(pd.DataFrame(syn_result["rows"]).set_index("year").style.format("{:,.1f}"), use_container_width=True)

    # ===================================================== FOOTBALL FIELD ===
    with tab_ff:
        if fundamentals.get("week52_low") and fundamentals.get("week52_high"):
            mid = (fundamentals["week52_low"] + fundamentals["week52_high"]) / 2
            valuation_ranges[t("ma_ff_52week")] = (fundamentals["week52_low"], mid, fundamentals["week52_high"])

        if not valuation_ranges:
            st.info(t("ma_ff_empty"))
        else:
            fig = go.Figure()
            labels = list(valuation_ranges.keys())
            for label in labels:
                low, mid, high = valuation_ranges[label]
                fig.add_trace(go.Scatter(
                    x=[low, high], y=[label, label], mode="lines+markers",
                    line=dict(color="#f17909", width=8), marker=dict(size=10, color="#f17909"),
                    showlegend=False,
                ))
                fig.add_trace(go.Scatter(
                    x=[mid], y=[label], mode="markers", marker=dict(size=12, color="#111111", symbol="line-ns-open"),
                    showlegend=False,
                ))
            if current_price:
                fig.add_vline(x=current_price, line_dash="dash", line_color="#0e21a2",
                               annotation_text=t("ma_ff_current_price"))
            fig.update_layout(height=350, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
                               xaxis_title=t("ma_ff_xaxis"))
            st.plotly_chart(fig, use_container_width=True)
            st.caption(t("ma_ff_caption"))


# ================================================================== APP ===
def render_portfolio_page():
    if st.button(t("back_to_finance")):
        st.session_state["page"] = "finance_home"
        st.rerun()
    st.image("logo_wordmark.svg", width=260)
    st.caption(t("tagline"))

    saved = load_last_portfolio()

    with st.sidebar:
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
page = st.session_state["page"]
if page == "finance_home":
    render_finance_home()
elif page == "portfolio":
    render_portfolio_page()
elif page == "cib":
    render_coming_soon("logo_cib101.svg")
elif page == "ma":
    render_ma_page()
