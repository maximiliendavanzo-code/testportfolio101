"""
Traductions de l'interface (FR / EN) et petit utilitaire de sélection de langue.
"""
import streamlit as st

TRANSLATIONS = {
    "tagline": {
        "fr": "Performance historique · corrélation · volatilité · VaR · Expected Shortfall — données réelles via Yahoo Finance",
        "en": "Historical performance · correlation · volatility · VaR · Expected Shortfall — real data via Yahoo Finance",
    },
    # ---- page d'accueil ----
    "home_subtitle": {
        "fr": "Comprenez vraiment le risque et la performance de votre portefeuille.",
        "en": "Truly understand your portfolio's risk and performance.",
    },
    "home_description": {
        "fr": "Portfolio101 se connecte à Yahoo Finance pour récupérer l'historique réel de vos actions et ETF, "
              "convertit tout dans la devise de votre choix, puis calcule automatiquement la performance, "
              "la corrélation entre vos actifs, la volatilité et des indicateurs de risque comme la VaR et "
              "l'Expected Shortfall. Vous repartez avec des résultats clairs, exportables en Excel, image ou PDF.",
        "en": "Portfolio101 connects to Yahoo Finance to fetch the real historical prices of your stocks and ETFs, "
              "converts everything into the currency of your choice, then automatically computes performance, "
              "correlation between your assets, volatility, and risk metrics like VaR and Expected Shortfall. "
              "You get clear results, exportable to Excel, image, or PDF.",
    },
    "home_feature_1_title": {"fr": "Données réelles", "en": "Real data"},
    "home_feature_1_text": {
        "fr": "Historique de n'importe quelle action ou ETF coté, récupéré en direct.",
        "en": "Historical data for any listed stock or ETF, fetched live.",
    },
    "home_feature_2_title": {"fr": "Analyse de risque", "en": "Risk analysis"},
    "home_feature_2_text": {
        "fr": "Volatilité, VaR, Expected Shortfall, corrélation entre actifs.",
        "en": "Volatility, VaR, Expected Shortfall, correlation between assets.",
    },
    "home_feature_3_title": {"fr": "Multi-devises", "en": "Multi-currency"},
    "home_feature_3_text": {
        "fr": "Convertissez automatiquement tous vos actifs dans une seule devise.",
        "en": "Automatically convert all your assets into a single currency.",
    },
    "home_cta": {"fr": "Commencer →", "en": "Get started →"},

    # ---- barre latérale ----
    "sidebar_header": {"fr": "Composition du portefeuille", "en": "Portfolio composition"},
    "back_home": {"fr": "← Accueil", "en": "← Home"},
    "tickers_label": {"fr": "Tickers", "en": "Tickers"},
    "tickers_help": {
        "fr": "Choisissez dans la liste ou tapez un symbole Yahoo Finance personnalisé puis validez avec Entrée "
              "(ex: MC.PA pour LVMH, CW8.PA pour un ETF MSCI World).",
        "en": "Pick from the list or type a custom Yahoo Finance symbol and press Enter "
              "(e.g. MC.PA for LVMH, CW8.PA for an MSCI World ETF).",
    },
    "currency_subheader": {"fr": "Devise du portefeuille", "en": "Portfolio currency"},
    "currency_label": {"fr": "Convertir tous les actifs en", "en": "Convert all assets to"},
    "currency_help": {
        "fr": "Chaque actif est automatiquement converti depuis sa devise native vers celle-ci, via les taux de change historiques.",
        "en": "Each asset is automatically converted from its native currency into this one, using historical exchange rates.",
    },
    "period_subheader": {"fr": "Période", "en": "Period"},
    "start_label": {"fr": "Début", "en": "Start"},
    "end_label": {"fr": "Fin", "en": "End"},
    "freq_label": {"fr": "Fréquence des données", "en": "Data frequency"},
    "freq_help": {
        "fr": "La fréquence à laquelle les rendements sont mesurés. Influence l'annualisation des indicateurs.",
        "en": "The frequency at which returns are measured. Affects the annualization of the metrics.",
    },
    "freq_daily": {"fr": "Quotidienne", "en": "Daily"},
    "freq_weekly": {"fr": "Hebdomadaire", "en": "Weekly"},
    "freq_monthly": {"fr": "Mensuelle", "en": "Monthly"},
    "weights_subheader": {"fr": "Pondérations", "en": "Weights"},
    "weights_caption": {
        "fr": "Doit sommer à exactement 100% pour lancer l'analyse.",
        "en": "Must add up to exactly 100% to run the analysis.",
    },
    "equal_weight_button": {"fr": "⚖️ Répartir équitablement", "en": "⚖️ Distribute equally"},
    "weights_ok": {"fr": "Total des pondérations : {total:.1f}% ✓", "en": "Total weight: {total:.1f}% ✓"},
    "weights_error": {
        "fr": "Total des pondérations : {total:.1f}% — doit être exactement 100% pour lancer l'analyse.",
        "en": "Total weight: {total:.1f}% — must be exactly 100% to run the analysis.",
    },
    "risk_subheader": {"fr": "Paramètres de risque", "en": "Risk settings"},
    "riskfree_label": {"fr": "Taux sans risque annuel (%)", "en": "Annual risk-free rate (%)"},
    "riskfree_help": {
        "fr": "Rendement d'un placement considéré sans risque (ex: taux d'un livret ou d'une obligation d'État). "
              "Sert de référence pour calculer le ratio de Sharpe.",
        "en": "Return of an investment considered risk-free (e.g. a savings account or government bond rate). "
              "Used as the reference to compute the Sharpe ratio.",
    },
    "confidence_label": {"fr": "Niveau de confiance (VaR / ES)", "en": "Confidence level (VaR / ES)"},
    "confidence_help": {
        "fr": "Le seuil de probabilité utilisé pour la VaR et l'Expected Shortfall. 95% = on regarde les 5% pires cas.",
        "en": "The probability threshold used for VaR and Expected Shortfall. 95% = looking at the worst 5% of cases.",
    },
    "analyze_button": {"fr": "🔎 Analyser le portefeuille", "en": "🔎 Analyze portfolio"},
    "inflation_subheader": {"fr": "Inflation", "en": "Inflation"},
    "inflation_toggle": {"fr": "Ajuster les résultats à l'inflation réelle", "en": "Adjust results for real inflation"},
    "inflation_help": {
        "fr": "Si activé, tous les indicateurs (performance, CAGR, volatilité, VaR...) sont calculés en termes réels, "
              "en utilisant l'inflation réellement constatée mois par mois sur la période (indice des prix officiel "
              "de la devise du portefeuille), pas un taux supposé.",
        "en": "If enabled, all metrics (performance, CAGR, volatility, VaR...) are computed in real terms, "
              "using the actual month-by-month inflation observed over the period (official price index "
              "of the portfolio's currency), not an assumed rate.",
    },
    "inflation_spinner": {"fr": "Récupération des données d'inflation…", "en": "Fetching inflation data…"},
    "inflation_unavailable_warning": {
        "fr": "Données d'inflation indisponibles pour {ccy} sur cette période — résultats affichés en termes nominaux.",
        "en": "Inflation data unavailable for {ccy} over this period — results shown in nominal terms.",
    },
    "real_terms_note": {
        "fr": "📉 Résultats en **termes réels**, ajustés de l'inflation constatée en {ccy} (indice des prix officiel) "
              "— {rate:.1f}%/an en moyenne annualisée sur la période.",
        "en": "📉 Results in **real terms**, adjusted for observed inflation in {ccy} (official price index) "
              "— {rate:.1f}%/year on average (annualized) over the period.",
    },
    "nominal_terms_note": {
        "fr": "Résultats en termes nominaux (non ajustés de l'inflation).",
        "en": "Results in nominal terms (not adjusted for inflation).",
    },

    # ---- corps principal ----
    "no_ticker_info": {
        "fr": "👈 Ajoutez au moins un ticker dans la barre latérale pour commencer.",
        "en": "👈 Add at least one ticker in the sidebar to get started.",
    },
    "composition_expander": {"fr": "Composition sélectionnée", "en": "Selected composition"},
    "weights_warning_relaunch": {
        "fr": "Ajustez les pondérations à exactement 100% dans la barre latérale pour relancer l'analyse.",
        "en": "Adjust the weights to exactly 100% in the sidebar to rerun the analysis.",
    },
    "fetching_spinner": {"fr": "Récupération des données Yahoo Finance…", "en": "Fetching data from Yahoo Finance…"},
    "fetch_error": {"fr": "Erreur lors de la récupération des données : {e}", "en": "Error while fetching data: {e}"},
    "missing_tickers_warning": {
        "fr": "Ticker(s) introuvable(s) ou sans données sur cette période : {tickers}",
        "en": "Ticker(s) not found or with no data for this period: {tickers}",
    },
    "min_2_tickers_error": {
        "fr": "Il faut au moins 2 tickers valides avec des données pour calculer la corrélation et les autres métriques.",
        "en": "At least 2 valid tickers with data are required to compute correlation and other metrics.",
    },
    "converting_spinner": {"fr": "Conversion des devises…", "en": "Converting currencies…"},
    "fx_not_found_warning": {
        "fr": "Taux de change introuvable pour : {tickers} — prix laissés dans leur devise native, ce qui fausse la comparaison.",
        "en": "Exchange rate not found for: {tickers} — prices left in their native currency, which skews the comparison.",
    },
    "currency_details_expander": {"fr": "Détail des conversions de devise", "en": "Currency conversion details"},
    "not_enough_data_error": {
        "fr": "Pas assez de points de données sur la période/fréquence choisie. Élargissez la période.",
        "en": "Not enough data points for the chosen period/frequency. Widen the date range.",
    },
    "metrics_subheader": {"fr": "Indicateurs de performance et de risque", "en": "Performance and risk metrics"},
    "metric_total_return": {"fr": "Rendement total", "en": "Total return"},
    "metric_total_return_help": {
        "fr": "Variation totale de la valeur du portefeuille entre le début et la fin de la période.",
        "en": "Total change in portfolio value between the start and end of the period.",
    },
    "metric_cagr": {"fr": "CAGR (annualisé)", "en": "CAGR (annualized)"},
    "metric_cagr_help": {
        "fr": "Taux de croissance annuel moyen composé : le rendement annuel constant qui aurait produit le même résultat final.",
        "en": "Compound annual growth rate: the constant yearly return that would have produced the same final result.",
    },
    "metric_vol": {"fr": "Volatilité annualisée", "en": "Annualized volatility"},
    "metric_vol_help": {
        "fr": "Ampleur des variations du portefeuille dans le temps, ramenée à une base annuelle. Plus c'est élevé, plus le portefeuille est instable.",
        "en": "Magnitude of the portfolio's fluctuations over time, annualized. The higher it is, the more unstable the portfolio.",
    },
    "metric_sharpe": {"fr": "Ratio de Sharpe", "en": "Sharpe ratio"},
    "metric_sharpe_help": {
        "fr": "Rendement obtenu par unité de risque prise, au-delà du taux sans risque. Plus il est élevé, meilleur est le couple rendement/risque.",
        "en": "Return earned per unit of risk taken, above the risk-free rate. The higher, the better the risk/return trade-off.",
    },
    "metric_mdd": {"fr": "Max drawdown", "en": "Max drawdown"},
    "metric_mdd_help": {
        "fr": "La plus grosse perte subie entre un sommet et le creux suivant sur la période — le pire scénario réellement vécu.",
        "en": "The largest loss from a peak to the following trough over the period — the actual worst-case scenario experienced.",
    },
    "metric_var_hist": {"fr": "VaR historique ({conf}%)", "en": "Historical VaR ({conf}%)"},
    "metric_var_hist_help": {
        "fr": "Perte maximale attendue par période, avec le niveau de confiance choisi (calculée directement sur l'historique des rendements).",
        "en": "Maximum expected loss per period, at the chosen confidence level (computed directly from historical returns).",
    },
    "metric_es": {"fr": "Expected Shortfall ({conf}%)", "en": "Expected Shortfall ({conf}%)"},
    "metric_es_help": {
        "fr": "Perte moyenne dans les pires cas au-delà de la VaR — répond à \"si ça tourne mal, en moyenne je perds combien ?\".",
        "en": "Average loss in the worst-case scenarios beyond the VaR — answers \"if things go badly, how much do I lose on average?\".",
    },
    "metric_var_param": {"fr": "VaR paramétrique ({conf}%)", "en": "Parametric VaR ({conf}%)"},
    "metric_var_param_help": {
        "fr": "Même idée que la VaR historique, mais calculée en supposant que les rendements suivent une loi normale.",
        "en": "Same idea as historical VaR, but computed assuming returns follow a normal distribution.",
    },
    "performance_subheader": {"fr": "Performance cumulée (base 100, en {ccy})", "en": "Cumulative performance (base 100, in {ccy})"},
    "portfolio_label": {"fr": "Portefeuille", "en": "Portfolio"},
    "correlation_subheader": {"fr": "Matrice de corrélation", "en": "Correlation matrix"},
    "correlation_caption": {
        "fr": "Corrélation des rendements entre chaque paire d'actifs (-1 à +1). Proche de 1 = évoluent ensemble, proche de -1 = évoluent en sens inverse, proche de 0 = pas de lien.",
        "en": "Correlation of returns between each pair of assets (-1 to +1). Near 1 = move together, near -1 = move oppositely, near 0 = no relationship.",
    },
    "distribution_subheader": {"fr": "Distribution des rendements", "en": "Return distribution"},
    "distribution_caption": {
        "fr": "Fréquence des rendements observés par période. La ligne pointillée marque le seuil de la VaR.",
        "en": "Frequency of observed returns per period. The dashed line marks the VaR threshold.",
    },
    "footer_caption": {
        "fr": "Basé sur {n} périodes ({freq}) entre {start} et {end}, tous les actifs convertis en {ccy}. "
              "Portefeuille simulé en buy-and-hold (sans rééquilibrage). Performances passées, ne préjugent pas "
              "des performances futures. Ceci n'est pas un conseil en investissement.",
        "en": "Based on {n} periods ({freq}) between {start} and {end}, all assets converted to {ccy}. "
              "Portfolio simulated buy-and-hold (no rebalancing). Past performance does not guarantee future results. "
              "This is not investment advice.",
    },
    "export_subheader": {"fr": "Exporter les résultats", "en": "Export results"},
    "export_excel": {"fr": "📊 Télécharger en Excel", "en": "📊 Download as Excel"},
    "export_png": {"fr": "🖼️ Télécharger le graphique (PNG)", "en": "🖼️ Download chart (PNG)"},
    "export_pdf": {"fr": "📄 Télécharger le rapport PDF", "en": "📄 Download PDF report"},
}

LANGUAGE_LABELS = {"fr": "🇫🇷 Français", "en": "🇬🇧 English"}


def t(key: str, **kwargs) -> str:
    """Traduit une clé dans la langue actuellement sélectionnée (session_state['lang'], 'fr' par défaut)."""
    lang = st.session_state.get("lang", "fr")
    text = TRANSLATIONS.get(key, {}).get(lang, TRANSLATIONS.get(key, {}).get("fr", key))
    return text.format(**kwargs) if kwargs else text


def render_language_selector():
    """Affiche un sélecteur de langue aligné en haut à droite de la page."""
    st.session_state.setdefault("lang", "fr")
    _, col_lang = st.columns([6, 1])
    with col_lang:
        choice = st.selectbox(
            "lang", options=list(LANGUAGE_LABELS.keys()), format_func=lambda k: LANGUAGE_LABELS[k],
            index=list(LANGUAGE_LABELS.keys()).index(st.session_state["lang"]),
            key="lang_selector", label_visibility="collapsed",
        )
    if choice != st.session_state["lang"]:
        st.session_state["lang"] = choice
        st.rerun()
