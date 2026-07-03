"""
Moteur de calcul pour M&A101 — reconstruit dans l'esprit d'un vrai modèle de deal
(DCF à convention mid-year, BFR en jours, synergies de revenus, structuration de
l'offre, financement, accretion/dilution du BPA, capacité d'endettement).
"""
import numpy as np
import pandas as pd


# ========================================================= TRAJECTOIRES =====
def build_growth_path(flat_rate: float, terminal_rate: float, n_years: int, n_flat_years: int) -> list:
    """n_flat_years à flat_rate, puis convergence linéaire vers terminal_rate sur le reste des années."""
    n_flat_years = min(n_flat_years, n_years)
    path = [flat_rate] * n_flat_years
    n_fade_years = n_years - n_flat_years
    for i in range(1, n_fade_years + 1):
        rate = flat_rate + (terminal_rate - flat_rate) * i / n_fade_years
        path.append(rate)
    return path


def build_converging_path(start_value: float, end_value: float, n_years: int) -> list:
    """Interpolation linéaire de start_value à end_value sur n_years (ex : D&A qui converge vers le Capex)."""
    if n_years == 1:
        return [end_value]
    return [start_value + (end_value - start_value) * i / (n_years - 1) for i in range(n_years)]


def _as_path(value, n: int) -> list:
    """Accepte un scalaire (répété n fois) ou une liste déjà de longueur n."""
    if isinstance(value, (list, tuple)):
        if len(value) != n:
            raise ValueError(f"La liste fournie a {len(value)} éléments, {n} attendus.")
        return list(value)
    return [value] * n


# ============================================================== WACC =====
def compute_cost_of_equity(risk_free_rate: float, beta: float, equity_risk_premium: float) -> float:
    """CAPM : coût des fonds propres = taux sans risque + beta x prime de risque actions."""
    return risk_free_rate + beta * equity_risk_premium


def compute_wacc(risk_free_rate: float, beta: float, equity_risk_premium: float,
                  cost_of_debt_pretax: float, tax_rate: float,
                  market_cap: float, net_debt: float) -> dict:
    """Coût moyen pondéré du capital, pondéré par la structure de capital actuelle."""
    cost_of_equity = compute_cost_of_equity(risk_free_rate, beta, equity_risk_premium)
    net_debt = max(net_debt, 0)
    total_capital = market_cap + net_debt
    weight_equity = market_cap / total_capital if total_capital > 0 else 1.0
    weight_debt = 1 - weight_equity
    cost_of_debt_after_tax = cost_of_debt_pretax * (1 - tax_rate)
    wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt_after_tax
    return {
        "cost_of_equity": cost_of_equity,
        "cost_of_debt_after_tax": cost_of_debt_after_tax,
        "weight_equity": weight_equity,
        "weight_debt": weight_debt,
        "wacc": wacc,
    }


# =============================================================== DCF =====
def compute_dcf(base_revenue: float, revenue_growth_rates: list, ebitda_margin,
                 da_pct_revenue, capex_pct_revenue, tax_rate: float, wacc: float,
                 nwc_mode: str = "days", nwc_days: float = 60.0, nwc_pct_revenue: float = 0.0,
                 mid_year: bool = True,
                 terminal_method: str = "growth", terminal_growth: float = 0.02, exit_multiple: float = 8.0,
                 net_debt: float = 0.0, shares_outstanding: float = 1.0) -> dict:
    """
    DCF à 2 étapes (période explicite + valeur terminale), convention mid-year par défaut
    (comme en pratique bancaire : on suppose des flux reçus en moyenne au milieu de l'année).

    revenue_growth_rates : liste de taux (un par année explicite) — utiliser build_growth_path
    pour une trajectoire qui ralentit progressivement vers le taux terminal.
    ebitda_margin, da_pct_revenue, capex_pct_revenue : scalaire (constant) ou liste (un par année).
    nwc_mode : "days" (BFR = nwc_days/365 x CA, plus réaliste) ou "pct_delta" (BFR = % du delta de CA, plus simple).
    """
    n = len(revenue_growth_rates)
    margins = _as_path(ebitda_margin, n)
    da_pcts = _as_path(da_pct_revenue, n)
    capex_pcts = _as_path(capex_pct_revenue, n)

    rows = []
    prev_revenue = base_revenue
    prev_nwc = (nwc_days / 365 * base_revenue) if nwc_mode == "days" else 0.0
    pv_fcf_sum = 0.0
    for i in range(n):
        revenue = prev_revenue * (1 + revenue_growth_rates[i])
        ebitda = revenue * margins[i]
        da = revenue * da_pcts[i]
        ebit = ebitda - da
        tax = max(ebit, 0) * tax_rate
        nopat = ebit - tax
        capex = revenue * capex_pcts[i]

        if nwc_mode == "days":
            nwc_level = nwc_days / 365 * revenue
            delta_nwc = nwc_level - prev_nwc
            prev_nwc = nwc_level
        else:
            delta_nwc = nwc_pct_revenue * (revenue - prev_revenue)

        fcf = nopat + da - capex - delta_nwc
        period = (i + 1) - 0.5 if mid_year else (i + 1)
        discount_factor = 1 / (1 + wacc) ** period
        pv_fcf = fcf * discount_factor
        pv_fcf_sum += pv_fcf
        rows.append({
            "year": i + 1, "revenue": revenue, "ebitda": ebitda, "ebit": ebit,
            "nopat": nopat, "capex": capex, "delta_nwc": delta_nwc, "fcf": fcf,
            "discount_period": period, "discount_factor": discount_factor, "pv_fcf": pv_fcf,
        })
        prev_revenue = revenue

    last = rows[-1]
    if terminal_method == "exit_multiple":
        terminal_value = last["ebitda"] * exit_multiple
    else:
        if wacc <= terminal_growth:
            raise ValueError("Le WACC doit être strictement supérieur au taux de croissance terminal.")
        terminal_value = last["fcf"] * (1 + terminal_growth) / (wacc - terminal_growth)

    terminal_period = last["discount_period"]  # on actualise la VT au même facteur que le dernier flux explicite
    pv_terminal_value = terminal_value / (1 + wacc) ** terminal_period

    enterprise_value = pv_fcf_sum + pv_terminal_value
    equity_value = enterprise_value - net_debt
    value_per_share = equity_value / shares_outstanding if shares_outstanding else None

    return {
        "rows": rows,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "pv_fcf_sum": pv_fcf_sum,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "terminal_value_pct_of_ev": pv_terminal_value / enterprise_value if enterprise_value else None,
    }


def dcf_sensitivity(base_revenue, revenue_growth_rates, ebitda_margin, da_pct_revenue, capex_pct_revenue,
                     tax_rate, wacc_range: list, growth_range: list, net_debt: float, shares_outstanding: float,
                     nwc_mode: str = "days", nwc_days: float = 60.0, nwc_pct_revenue: float = 0.0,
                     mid_year: bool = True) -> pd.DataFrame:
    """Tableau de sensibilité valeur par action, WACC (lignes) x croissance terminale (colonnes)."""
    table = pd.DataFrame(index=wacc_range, columns=growth_range, dtype=float)
    for w in wacc_range:
        for g in growth_range:
            if g >= w:
                table.loc[w, g] = np.nan
                continue
            res = compute_dcf(base_revenue, revenue_growth_rates, ebitda_margin, da_pct_revenue,
                               capex_pct_revenue, tax_rate, w, nwc_mode, nwc_days, nwc_pct_revenue, mid_year,
                               terminal_method="growth", terminal_growth=g,
                               net_debt=net_debt, shares_outstanding=shares_outstanding)
            table.loc[w, g] = res["value_per_share"]
    return table


# ================================================ MULTIPLES (comps / transactions) ===
def implied_valuation_from_multiples(multiples: list, metric_value: float,
                                      net_debt: float, shares_outstanding: float) -> dict:
    """
    Applique une distribution de multiples (comparables boursiers ou transactions précédentes)
    à un indicateur de la cible (EBITDA ou Revenue). Bande basse/haute = 25e/75e percentile.
    """
    if not multiples:
        return None
    arr = np.array(multiples, dtype=float)
    stats = {
        "low": float(np.percentile(arr, 25)), "median": float(np.median(arr)),
        "high": float(np.percentile(arr, 75)), "min": float(arr.min()), "max": float(arr.max()), "n": len(arr),
    }
    results = {}
    for label in ["low", "median", "high"]:
        multiple = stats[label]
        ev = multiple * metric_value
        equity_value = ev - net_debt
        per_share = equity_value / shares_outstanding if shares_outstanding else None
        results[label] = {"multiple": multiple, "ev": ev, "equity_value": equity_value, "per_share": per_share}
    return {"stats": stats, "valuation": results}


# ============================================== SYNERGIES DE COÛTS (régime fixe) =====
def compute_cost_synergies_npv(annual_pretax_synergies: float, phase_in: list, tax_rate: float,
                                discount_rate: float, terminal_growth: float = 0.0) -> dict:
    """VAN de synergies de coûts après impôt : montée en puissance explicite puis perpétuité du régime de croisière."""
    rows = []
    pv_sum = 0.0
    for i, pct in enumerate(phase_in):
        pretax = annual_pretax_synergies * pct
        aftertax = pretax * (1 - tax_rate)
        discount_factor = 1 / (1 + discount_rate) ** (i + 1)
        pv = aftertax * discount_factor
        pv_sum += pv
        rows.append({"year": i + 1, "phase_in_pct": pct, "pretax": pretax, "aftertax": aftertax, "pv": pv})

    run_rate_aftertax = annual_pretax_synergies * (1 - tax_rate)
    if discount_rate <= terminal_growth:
        raise ValueError("Le taux d'actualisation doit être supérieur au taux de croissance terminal des synergies.")
    terminal_value = run_rate_aftertax * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_terminal_value = terminal_value / (1 + discount_rate) ** len(phase_in)

    return {"rows": rows, "pv_explicit_sum": pv_sum, "terminal_value": terminal_value,
            "pv_terminal_value": pv_terminal_value, "npv": pv_sum + pv_terminal_value}


# ============================================= SYNERGIES DE REVENUS (uplift + marge) ===
def compute_revenue_synergies_npv(base_revenue: float, standalone_growth_path: list, standalone_margin_path: list,
                                   synergy_growth_uplift, synergy_margin_uplift,
                                   tax_rate: float, wacc: float, terminal_growth: float) -> dict:
    """
    Synergies de revenus : la combinaison génère un CA qui croît plus vite (uplift de croissance)
    et une marge EBIT meilleure (uplift de marge) que le scénario stand-alone. On calcule le
    NOPAT incrémental (post-impôt) actualisé, plus une valeur terminale Gordon-Shapiro.
    """
    n = len(standalone_growth_path)
    margins = _as_path(standalone_margin_path, n)
    growth_uplift = _as_path(synergy_growth_uplift, n)
    margin_uplift = _as_path(synergy_margin_uplift, n)

    rows = []
    prev_revenue_standalone = base_revenue
    prev_revenue_synergy = base_revenue
    pv_sum = 0.0
    for i in range(n):
        revenue_standalone = prev_revenue_standalone * (1 + standalone_growth_path[i])
        revenue_with_synergies = prev_revenue_synergy * (1 + standalone_growth_path[i] + growth_uplift[i])

        ebit_standalone = revenue_standalone * margins[i]
        ebit_with_synergies = revenue_with_synergies * (margins[i] + margin_uplift[i])
        ebit_improvement = ebit_with_synergies - ebit_standalone

        nopat_improvement = ebit_improvement * (1 - tax_rate)
        discount_factor = 1 / (1 + wacc) ** (i + 1)
        pv = nopat_improvement * discount_factor
        pv_sum += pv

        rows.append({
            "year": i + 1, "revenue_standalone": revenue_standalone, "revenue_with_synergies": revenue_with_synergies,
            "ebit_improvement": ebit_improvement, "nopat_improvement": nopat_improvement, "pv": pv,
        })
        prev_revenue_standalone = revenue_standalone
        prev_revenue_synergy = revenue_with_synergies

    last_nopat_improvement = rows[-1]["nopat_improvement"]
    if wacc <= terminal_growth:
        raise ValueError("Le WACC doit être strictement supérieur au taux de croissance terminal.")
    terminal_value = last_nopat_improvement * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal_value = terminal_value / (1 + wacc) ** n

    return {"rows": rows, "pv_explicit_sum": pv_sum, "terminal_value": terminal_value,
            "pv_terminal_value": pv_terminal_value, "npv": pv_sum + pv_terminal_value}


# ==================================================== PRIME ET PRIX D'OFFRE =====
def compute_offer_price(current_price: float, premium_components: dict) -> dict:
    """
    Combine plusieurs composantes de prime, additionnées puis appliquées en une fois
    (ex {"Prime de base": 0.25, "Ajustement de sous-valorisation": 0.05, "Prime actionnaire stratégique": 0.05}
    -> prime totale 35%, prix = cours x 1.35).
    """
    total_premium = sum(premium_components.values())
    offer_price = current_price * (1 + total_premium)
    return {"offer_price": offer_price, "total_premium": total_premium, "multiplier": 1 + total_premium}


# ============================================== FINANCEMENT ET STRUCTURATION =====
def compute_blended_debt_rate(tranches: list) -> float:
    """tranches : [{'amount':1000,'coupon':0.0245}, ...] -> taux moyen pondéré par les montants."""
    total = sum(t["amount"] for t in tranches)
    if total == 0:
        return 0.0
    return sum(t["amount"] * t["coupon"] for t in tranches) / total


def compute_deal_structure(offer_price_per_share: float, target_shares_outstanding: float,
                            target_net_debt: float, deal_fees: float, cash_pct: float) -> dict:
    """Valeur du deal et répartition cash / dette nouvelle."""
    equity_value = offer_price_per_share * target_shares_outstanding
    total_deal_value = equity_value + target_net_debt + deal_fees
    cash_financed = total_deal_value * cash_pct
    debt_financed = total_deal_value * (1 - cash_pct)
    return {
        "equity_value": equity_value, "total_deal_value": total_deal_value,
        "cash_financed": cash_financed, "debt_financed": debt_financed,
    }


# =========================================================== EPS ACCRETION/DILUTION =====
def compute_eps_accretion_dilution(acquirer_net_income: float, target_net_income: float,
                                    synergies_pretax: float, new_debt_amount: float,
                                    new_debt_pretax_rate: float, tax_rate: float,
                                    acquirer_shares_outstanding: float, new_shares_issued: float = 0.0) -> dict:
    """Impact du deal sur le BPA de l'acquéreur (100% cash par défaut si new_shares_issued=0)."""
    interest_expense_aftertax = new_debt_amount * new_debt_pretax_rate * (1 - tax_rate)
    synergies_aftertax = synergies_pretax * (1 - tax_rate)
    pro_forma_net_income = acquirer_net_income + target_net_income + synergies_aftertax - interest_expense_aftertax
    pro_forma_shares = acquirer_shares_outstanding + new_shares_issued

    standalone_eps = acquirer_net_income / acquirer_shares_outstanding if acquirer_shares_outstanding else None
    pro_forma_eps = pro_forma_net_income / pro_forma_shares if pro_forma_shares else None
    accretion_dilution = (pro_forma_eps - standalone_eps) if (standalone_eps is not None and pro_forma_eps is not None) else None
    accretion_dilution_pct = (accretion_dilution / standalone_eps) if (accretion_dilution is not None and standalone_eps) else None

    return {
        "pro_forma_net_income": pro_forma_net_income, "standalone_eps": standalone_eps,
        "pro_forma_eps": pro_forma_eps, "accretion_dilution": accretion_dilution,
        "accretion_dilution_pct": accretion_dilution_pct, "interest_expense_aftertax": interest_expense_aftertax,
    }


# ============================================================ CAPACITE D'ENDETTEMENT =====
def compute_leverage(net_debt: float, ebitda: float):
    return net_debt / ebitda if ebitda else None


def compute_post_deal_leverage(acquirer_debt_pre: float, acquirer_cash_pre: float, new_debt_issued: float,
                                cash_used_for_deal: float, acquirer_ebitda: float, target_ebitda: float,
                                run_rate_synergy_ebitda: float = 0.0) -> dict:
    """Endettement avant/après deal, et EBITDA pro forma (acquéreur + cible + synergies en régime)."""
    total_debt_post = acquirer_debt_pre + new_debt_issued
    cash_post = max(acquirer_cash_pre - cash_used_for_deal, 0)
    net_debt_post = total_debt_post - cash_post
    pro_forma_ebitda = acquirer_ebitda + target_ebitda + run_rate_synergy_ebitda
    return {
        "net_debt_pre": acquirer_debt_pre - acquirer_cash_pre,
        "leverage_pre": compute_leverage(acquirer_debt_pre - acquirer_cash_pre, acquirer_ebitda),
        "net_debt_post": net_debt_post, "pro_forma_ebitda": pro_forma_ebitda,
        "leverage_post": compute_leverage(net_debt_post, pro_forma_ebitda),
    }
