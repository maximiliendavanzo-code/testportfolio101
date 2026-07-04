"""
Traductions de l'interface (FR / EN) et petit utilitaire de sélection de langue.
"""
import streamlit as st

TRANSLATIONS = {
    "tagline": {
        "fr": "Performance historique · corrélation · volatilité · VaR · Expected Shortfall — données réelles via Yahoo Finance",
        "en": "Historical performance · correlation · volatility · VaR · Expected Shortfall — real data via Yahoo Finance",
    },
    # ---- page d'accueil Finance101 ----
    "finance_home_subtitle": {
        "fr": "Trois outils, une seule plateforme, pour analyser vos décisions financières.",
        "en": "Three tools, one platform, to analyze your financial decisions.",
    },
    "finance_home_description": {
        "fr": "Simulez, comparez et comprenez vos décisions financières à partir de données réelles.",
        "en": "Simulate, compare, and understand your financial decisions using real data.",
    },
    "stat_1_label": {"fr": "+100", "en": "+100"},
    "stat_1_caption": {"fr": "Actifs analysables", "en": "Analyzable assets"},
    "stat_2_label": {"fr": "Données", "en": "Data"},
    "stat_2_caption": {"fr": "Réelles & à jour", "en": "Real & up to date"},
    "stat_3_label": {"fr": "Performance", "en": "Performance"},
    "stat_3_caption": {"fr": "Et risque avancés", "en": "And advanced risk"},
    "hero_panel_title": {"fr": "Performance du portefeuille", "en": "Portfolio performance"},
    "hero_return_label": {"fr": "Rendement", "en": "Return"},
    "hero_return_value": {"fr": "+12,45%", "en": "+12.45%"},
    "hero_vol_label": {"fr": "Volatilité", "en": "Volatility"},
    "hero_vol_value": {"fr": "11,32%", "en": "11.32%"},
    "hero_alloc_label": {"fr": "Allocation", "en": "Allocation"},
    "hero_risk_label": {"fr": "Analyse du risque", "en": "Risk analysis"},
    "tool_portfolio_desc": {
        "fr": "Analysez la performance et le risque de vos portefeuilles d'actions et d'ETF : corrélation, "
              "volatilité, VaR, Expected Shortfall, avec des données réelles.",
        "en": "Analyze the performance and risk of your stock and ETF portfolios: correlation, "
              "volatility, VaR, Expected Shortfall, with real data.",
    },
    "tool_cib_desc": {
        "fr": "Outils dédiés à la banque de financement et d'investissement.",
        "en": "Tools dedicated to corporate and investment banking.",
    },
    "tool_ma_desc": {
        "fr": "Outils dédiés à l'analyse de fusions-acquisitions.",
        "en": "Tools dedicated to mergers & acquisitions analysis.",
    },
    "tag_correlation": {"fr": "Corrélation", "en": "Correlation"},
    "tag_volatility": {"fr": "Volatilité", "en": "Volatility"},
    "tag_var": {"fr": "VaR", "en": "VaR"},
    "tag_es": {"fr": "Expected Shortfall", "en": "Expected Shortfall"},
    "tag_valuation": {"fr": "Valorisation", "en": "Valuation"},
    "tag_debt": {"fr": "Dette", "en": "Debt"},
    "tag_financing": {"fr": "Financement", "en": "Financing"},
    "tag_multiples": {"fr": "Multiples", "en": "Multiples"},
    "tag_synergies": {"fr": "Synergies", "en": "Synergies"},
    "tag_dealanalysis": {"fr": "Deal analysis", "en": "Deal analysis"},
    "cta_portfolio": {"fr": "Analyser un portefeuille →", "en": "Analyze a portfolio →"},
    "cta_cib": {"fr": "Explorer les outils CIB →", "en": "Explore CIB tools →"},
    "cta_ma": {"fr": "Analyser une opération →", "en": "Analyze a deal →"},
    "howitworks_title": {"fr": "Comment ça marche ?", "en": "How does it work?"},
    "howitworks_1_title": {"fr": "Choisissez un outil", "en": "Choose a tool"},
    "label_explication": {"fr": "Explication", "en": "Explanation"},
    "label_ex": {"fr": "Ex", "en": "E.g."},
    "howitworks_1_explication": {
        "fr": "Chaque outil correspond à un type d'analyse financière différent.",
        "en": "Each tool corresponds to a different type of financial analysis.",
    },
    "howitworks_1_ex": {
        "fr": "Portfolio101 pour un portefeuille d'actions, M&A101 pour une acquisition.",
        "en": "Portfolio101 for a stock portfolio, M&A101 for an acquisition.",
    },
    "howitworks_2_title": {"fr": "Entrez vos données", "en": "Enter your data"},
    "howitworks_2_explication": {
        "fr": "Renseignez les tickers, montants ou hypothèses nécessaires à l'analyse.",
        "en": "Enter the tickers, amounts, or assumptions needed for the analysis.",
    },
    "howitworks_2_ex": {
        "fr": "Le ticker \"AAPL\", ou une croissance de revenus de 8% par an.",
        "en": "The ticker \"AAPL\", or a revenue growth of 8% per year.",
    },
    "howitworks_3_title": {"fr": "Analysez les résultats", "en": "Analyze the results"},
    "howitworks_3_explication": {
        "fr": "Consultez les indicateurs calculés automatiquement à partir de vos données.",
        "en": "Review the indicators automatically computed from your data.",
    },
    "howitworks_3_ex": {
        "fr": "Rendement, volatilité, ou valeur par action.",
        "en": "Return, volatility, or value per share.",
    },
    "footer_text": {
        "fr": "Finance101 — Portfolio101, CIB101 et M&A101. Données réelles via Yahoo Finance. Ceci n'est pas un conseil en investissement.",
        "en": "Finance101 — Portfolio101, CIB101 and M&A101. Real data via Yahoo Finance. This is not investment advice.",
    },
    "open_button": {"fr": "Ouvrir →", "en": "Open →"},
    "coming_soon_badge": {"fr": "Bientôt disponible", "en": "Coming soon"},
    "coming_soon_text": {
        "fr": "Cet outil est en cours de construction. Revenez bientôt !",
        "en": "This tool is under construction. Check back soon!",
    },
    "back_to_finance": {"fr": "← Finance101", "en": "← Finance101"},

    # ---- M&A101 ----
    "ma_tagline": {
        "fr": "DCF · Comparables boursiers · Transactions précédentes · Synergies · Football field",
        "en": "DCF · Trading comps · Precedent transactions · Synergies · Football field",
    },
    "ma_target_subheader": {"fr": "Société cible", "en": "Target company"},
    "ma_target_mode": {"fr": "Comment renseigner la cible ?", "en": "How to enter the target?"},
    "ma_target_ticker": {"fr": "Ticker réel", "en": "Real ticker"},
    "ma_target_manual": {"fr": "Saisie manuelle", "en": "Manual entry"},
    "ma_ticker_label": {"fr": "Ticker Yahoo Finance", "en": "Yahoo Finance ticker"},
    "ma_ticker_help": {
        "fr": "Les champs ci-dessous se pré-remplissent avec les données réelles ; vous pouvez toujours les modifier.",
        "en": "The fields below are pre-filled with real data; you can still edit them.",
    },
    "ma_acquirer_expander": {"fr": "Modifier les données de l'acquéreur", "en": "Edit acquirer data"},
    "ma_acquirer_subheader": {"fr": "Société acquéreuse", "en": "Acquiring company"},
    "ma_netincome_label": {"fr": "Résultat net (M)", "en": "Net income (M)"},
    "ma_totaldebt_label": {"fr": "Dette brute (M)", "en": "Gross debt (M)"},
    "ma_totalcash_label": {"fr": "Trésorerie (M)", "en": "Cash (M)"},
    "ma_projection_years": {"fr": "Années de projection", "en": "Projection years"},
    "ma_flat_years": {"fr": "Années à croissance constante", "en": "Years at flat growth"},
    "ma_flatgrowth": {"fr": "Croissance initiale / an (%)", "en": "Initial growth / year (%)"},
    "ma_da_start": {"fr": "D&A initial (% du CA)", "en": "Initial D&A (% of revenue)"},
    "ma_nwcdays": {"fr": "BFR (jours de CA)", "en": "NWC (days of revenue)"},
    "ma_fcf_detail": {"fr": "Détail des flux de trésorerie", "en": "Cash flow detail"},
    "ma_ff_dcf_standalone": {"fr": "DCF stand-alone", "en": "DCF standalone"},
    "ma_ff_comps": {"fr": "Comparables boursiers", "en": "Trading comps"},
    "ma_ff_trans": {"fr": "Transactions précédentes", "en": "Precedent transactions"},
    "ma_ff_dcf_synergies": {"fr": "DCF avec synergies", "en": "DCF with synergies"},
    "ma_ff_research": {"fr": "Note d'analyste", "en": "Equity research"},
    "ma_ff_manual_range": {"fr": "Ajouter une fourchette manuelle (ex: notes d'analystes)", "en": "Add a manual range (e.g. analyst notes)"},
    "ma_ff_add_research": {"fr": "Ajouter une fourchette de notes d'analystes", "en": "Add an equity research range"},
    "ma_syn_mode": {"fr": "Type de synergies", "en": "Synergy type"},
    "ma_syn_mode_cost": {"fr": "Synergies de coûts", "en": "Cost synergies"},
    "ma_syn_mode_revenue": {"fr": "Synergies de revenus", "en": "Revenue synergies"},
    "ma_syn_growth_uplift": {"fr": "Uplift de croissance du CA (%)", "en": "Revenue growth uplift (%)"},
    "ma_syn_margin_uplift": {"fr": "Uplift de marge EBIT en régime (%)", "en": "Run-rate EBIT margin uplift (%)"},
    "ma_offer_premium_title": {"fr": "Composantes de la prime", "en": "Premium components"},
    "ma_offer_base_premium": {"fr": "Prime de base (%)", "en": "Base premium (%)"},
    "ma_offer_underval_premium": {"fr": "Ajustement de sous-valorisation (%)", "en": "Undervaluation adjustment (%)"},
    "ma_offer_strategic_premium": {"fr": "Prime actionnaire stratégique (%)", "en": "Strategic holder premium (%)"},
    "ma_offer_total_premium": {"fr": "Prime totale", "en": "Total premium"},
    "ma_offer_price_result": {"fr": "Prix d'offre par action", "en": "Offer price per share"},
    "ma_offer_range_title": {"fr": "Fourchette d'offre", "en": "Offer range"},
    "ma_offer_range_label": {"fr": "Scénario", "en": "Scenario"},
    "ma_offer_range_price": {"fr": "Prix", "en": "Price"},
    "ma_offer_range_premium": {"fr": "Prime vs cours actuel", "en": "Premium vs current price"},
    "ma_offer_current": {"fr": "Cours actuel", "en": "Current price"},
    "ma_offer_initial": {"fr": "Offre initiale", "en": "Initial offer"},
    "ma_offer_target": {"fr": "Offre cible", "en": "Target offer"},
    "ma_offer_walkaway": {"fr": "Prix plafond", "en": "Walk-away price"},
    "ma_fin_structure_title": {"fr": "Structure du financement", "en": "Financing structure"},
    "ma_fin_fees": {"fr": "Frais liés au deal (M)", "en": "Deal fees (M)"},
    "ma_fin_cash_pct": {"fr": "Part refinancée en cash (%)", "en": "Cash-refinanced portion (%)"},
    "ma_fin_equity_value": {"fr": "Valeur des fonds propres du deal", "en": "Deal equity value"},
    "ma_fin_total_value": {"fr": "Valeur totale du deal", "en": "Total deal value"},
    "ma_fin_debt_financed": {"fr": "Financé par nouvelle dette", "en": "Financed by new debt"},
    "ma_fin_tranches_title": {"fr": "Tranches de dette", "en": "Debt tranches"},
    "ma_fin_tranche": {"fr": "Tranche", "en": "Tranche"},
    "ma_fin_amount": {"fr": "Montant (M)", "en": "Amount (M)"},
    "ma_fin_coupon": {"fr": "Coupon (%)", "en": "Coupon (%)"},
    "ma_fin_blended_rate": {"fr": "Taux moyen pondéré", "en": "Blended rate"},
    "ma_eps_title": {"fr": "Impact sur le BPA de l'acquéreur", "en": "Impact on acquirer's EPS"},
    "ma_eps_standalone": {"fr": "BPA stand-alone", "en": "Standalone EPS"},
    "ma_eps_proforma": {"fr": "BPA pro forma", "en": "Pro forma EPS"},
    "ma_eps_impact": {"fr": "Accretion / dilution", "en": "Accretion / dilution"},
    "ma_tab_offer": {"fr": "Offre & Prime", "en": "Offer & Premium"},
    "ma_tab_fin": {"fr": "Financement & BPA", "en": "Financing & EPS"},
    "ma_tab_debt": {"fr": "Capacité d'endettement", "en": "Debt capacity"},
    "ma_debt_leverage_pre": {"fr": "Levier avant deal", "en": "Leverage pre-deal"},
    "ma_debt_leverage_post": {"fr": "Levier après deal", "en": "Leverage post-deal"},
    "ma_debt_netdebt_pre": {"fr": "Dette nette avant deal : {val:,.0f} M", "en": "Net debt pre-deal: {val:,.0f} M"},
    "ma_debt_netdebt_post": {"fr": "Dette nette après deal : {val:,.0f} M", "en": "Net debt post-deal: {val:,.0f} M"},
    "ma_debt_proforma_ebitda": {"fr": "EBITDA pro forma (acquéreur + cible + synergies) : {val:,.0f} M", "en": "Pro forma EBITDA (acquirer + target + synergies): {val:,.0f} M"},
    "ma_name_label": {"fr": "Nom de la société", "en": "Company name"},
    "ma_revenue_label": {"fr": "Chiffre d'affaires (M)", "en": "Revenue (M)"},
    "ma_units_help": {"fr": "En millions, dans la devise de la société.", "en": "In millions, company's currency."},
    "ma_ebitda_label": {"fr": "EBITDA (M)", "en": "EBITDA (M)"},
    "ma_netdebt_label": {"fr": "Dette nette (M)", "en": "Net debt (M)"},
    "ma_shares_label": {"fr": "Actions en circulation (millions)", "en": "Shares outstanding (millions)"},
    "ma_shares_help": {"fr": "Nombre total d'actions, en millions.", "en": "Total number of shares, in millions."},
    "ma_price_label": {"fr": "Cours actuel", "en": "Current price"},
    "ma_beta_label": {"fr": "Bêta", "en": "Beta"},
    "ma_marketcap_label": {"fr": "Capitalisation boursière (M)", "en": "Market capitalization (M)"},
    "ma_tab_dcf": {"fr": "DCF", "en": "DCF"},
    "ma_tab_comps": {"fr": "Comparables", "en": "Comps"},
    "ma_tab_trans": {"fr": "Transactions", "en": "Transactions"},
    "ma_tab_syn": {"fr": "Synergies", "en": "Synergies"},
    "ma_tab_ff": {"fr": "Football Field", "en": "Football Field"},
    "ma_dcf_assumptions": {"fr": "Hypothèses", "en": "Assumptions"},
    "ma_riskfree": {"fr": "Taux sans risque (%)", "en": "Risk-free rate (%)"},
    "ma_erp": {"fr": "Prime de risque actions (%)", "en": "Equity risk premium (%)"},
    "ma_costdebt": {"fr": "Coût de la dette avant impôt (%)", "en": "Pre-tax cost of debt (%)"},
    "ma_taxrate": {"fr": "Taux d'imposition (%)", "en": "Tax rate (%)"},
    "ma_revgrowth": {"fr": "Croissance du CA / an (%)", "en": "Revenue growth / year (%)"},
    "ma_ebitdamargin": {"fr": "Marge d'EBITDA (%)", "en": "EBITDA margin (%)"},
    "ma_dapct": {"fr": "D&A (% du CA)", "en": "D&A (% of revenue)"},
    "ma_capexpct": {"fr": "Capex (% du CA)", "en": "Capex (% of revenue)"},
    "ma_nwcpct": {"fr": "Variation du BFR (% du delta CA)", "en": "Change in NWC (% of revenue delta)"},
    "ma_terminal_method": {"fr": "Valeur terminale", "en": "Terminal value"},
    "ma_terminal_growth": {"fr": "Croissance perpétuelle", "en": "Perpetuity growth"},
    "ma_terminal_exit": {"fr": "Multiple de sortie", "en": "Exit multiple"},
    "ma_terminal_growth_rate": {"fr": "Taux de croissance terminal (%)", "en": "Terminal growth rate (%)"},
    "ma_exit_multiple": {"fr": "Multiple de sortie (EV/EBITDA)", "en": "Exit multiple (EV/EBITDA)"},
    "ma_wacc_result": {
        "fr": "WACC calculé : **{wacc:.2f}%** (coût des fonds propres : {coe:.2f}%)",
        "en": "Computed WACC: **{wacc:.2f}%** (cost of equity: {coe:.2f}%)",
    },
    "ma_ev_result": {"fr": "Valeur d'entreprise", "en": "Enterprise value"},
    "ma_equity_result": {"fr": "Valeur des fonds propres", "en": "Equity value"},
    "ma_pershare_result": {"fr": "Valeur par action", "en": "Value per share"},
    "ma_upside": {"fr": "Potentiel vs cours actuel : {upside:+.1f}%", "en": "Upside vs current price: {upside:+.1f}%"},
    "ma_sensitivity_title": {"fr": "Sensibilité (WACC × croissance terminale)", "en": "Sensitivity (WACC × terminal growth)"},
    "ma_peers_label": {"fr": "Sociétés comparables", "en": "Comparable companies"},
    "ma_peers_help": {"fr": "Choisissez des entreprises du même secteur, taille similaire.", "en": "Pick companies from the same sector, similar size."},
    "ma_range_low": {"fr": "Bas de fourchette", "en": "Low end"},
    "ma_range_median": {"fr": "Médiane", "en": "Median"},
    "ma_range_high": {"fr": "Haut de fourchette", "en": "High end"},
    "ma_not_enough_peers": {
        "fr": "Ajoutez au moins 2 comparables avec un EV/EBITDA disponible pour obtenir une fourchette.",
        "en": "Add at least 2 comparables with available EV/EBITDA to get a valuation range.",
    },
    "ma_trans_help": {
        "fr": "Saisissez les multiples EV/EBITDA de transactions M&A comparables connues (aucune source de données gratuite fiable pour cela).",
        "en": "Enter the EV/EBITDA multiples of known comparable M&A transactions (no reliable free data source for this).",
    },
    "ma_trans_deal": {"fr": "Deal", "en": "Deal"},
    "ma_not_enough_trans": {
        "fr": "Ajoutez au moins 2 transactions avec un multiple valide pour obtenir une fourchette.",
        "en": "Add at least 2 transactions with a valid multiple to get a valuation range.",
    },
    "ma_syn_amount": {"fr": "Synergies annuelles en régime (avant impôt)", "en": "Run-rate annual synergies (pre-tax)"},
    "ma_syn_discount": {"fr": "Taux d'actualisation (%)", "en": "Discount rate (%)"},
    "ma_syn_phasein_years": {"fr": "Années de montée en puissance", "en": "Phase-in years"},
    "ma_syn_phasein_display": {"fr": "Montée en puissance : {pct}", "en": "Phase-in: {pct}"},
    "ma_syn_npv": {"fr": "VAN des synergies", "en": "Synergies NPV"},
    "ma_syn_pershare": {"fr": "Valeur par action", "en": "Value per share"},
    "ma_ff_52week": {"fr": "Cours sur 52 semaines", "en": "52-week trading range"},
    "ma_ff_empty": {
        "fr": "Complétez au moins un onglet (DCF, Comparables, Transactions) pour voir le football field.",
        "en": "Complete at least one tab (DCF, Comps, Transactions) to see the football field.",
    },
    "ma_ff_current_price": {"fr": "Cours actuel", "en": "Current price"},
    "ma_ff_xaxis": {"fr": "Valeur par action", "en": "Value per share"},
    "ma_ff_caption": {
        "fr": "Le trait noir marque le point médian de chaque méthode ; la ligne pointillée bleue, le cours actuel.",
        "en": "The black tick marks the midpoint of each method; the dashed blue line is the current price.",
    },

    # ---- barre latérale ----
    "sidebar_header": {"fr": "Composition du portefeuille", "en": "Portfolio composition"},
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
    "ma_export_needs_dcf": {
        "fr": "Complétez au moins l'onglet DCF pour pouvoir exporter les résultats.",
        "en": "Complete at least the DCF tab to be able to export the results.",
    },
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
