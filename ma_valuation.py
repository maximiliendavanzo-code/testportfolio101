"""
Moteur de calcul pour M&A101 : DCF, valorisation par multiples (comparables
boursiers et transactions précédentes partagent la même logique), synergies,
et préparation des données pour le graphique football field.
"""
import numpy as np
import pandas as pd


# ============================================================== WACC =====
def compute_cost_of_equity(risk_free_rate: float, beta: float, equity_risk_premium: float) -> float:
    """CAPM : coût des fonds propres = taux sans risque + beta x prime de risque actions."""
    return risk_free_rate + beta * equity_risk_premium


def compute_wacc(risk_free_rate: float, beta: float, equity_risk_premium: float,
                  cost_of_debt_pretax: float, tax_rate: float,
                  market_cap: float, net_debt: float) -> dict:
    """Coût moyen pondéré du capital, pondéré par la structure de capital actuelle (capitaux propres / dette nette)."""
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
                 da_pct_revenue: float, capex_pct_revenue: float, nwc_pct_revenue: float,
                 tax_rate: float, wacc: float,
                 terminal_method: str = "growth", terminal_growth: float = 0.02, exit_multiple: float = 8.0,
                 net_debt: float = 0.0, shares_outstanding: float = 1.0) -> dict:
    """
    DCF à 2 étapes (période explicite + valeur terminale).
    ebitda_margin : un taux constant, ou une liste (un par année explicite).
    terminal_method : "growth" (Gordon Growth) ou "exit_multiple" (EV/EBITDA de sortie).
    """
    n = len(revenue_growth_rates)
    margins = ebitda_margin if isinstance(ebitda_margin, (list, tuple)) else [ebitda_margin] * n
    if len(margins) != n:
        raise ValueError("ebitda_margin doit avoir la même longueur que revenue_growth_rates si c'est une liste.")

    rows = []
    prev_revenue = base_revenue
    pv_fcf_sum = 0.0
    for i in range(n):
        revenue = prev_revenue * (1 + revenue_growth_rates[i])
        ebitda = revenue * margins[i]
        da = revenue * da_pct_revenue
        ebit = ebitda - da
        tax = max(ebit, 0) * tax_rate
        nopat = ebit - tax
        capex = revenue * capex_pct_revenue
        delta_nwc = nwc_pct_revenue * (revenue - prev_revenue)
        fcf = nopat + da - capex - delta_nwc
        discount_factor = 1 / (1 + wacc) ** (i + 1)
        pv_fcf = fcf * discount_factor
        pv_fcf_sum += pv_fcf
        rows.append({
            "year": i + 1, "revenue": revenue, "ebitda": ebitda, "ebit": ebit,
            "nopat": nopat, "capex": capex, "delta_nwc": delta_nwc, "fcf": fcf,
            "discount_factor": discount_factor, "pv_fcf": pv_fcf,
        })
        prev_revenue = revenue

    last = rows[-1]
    if terminal_method == "exit_multiple":
        terminal_value = last["ebitda"] * exit_multiple
    else:
        if wacc <= terminal_growth:
            raise ValueError("Le WACC doit être strictement supérieur au taux de croissance terminal.")
        terminal_value = last["fcf"] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal_value = terminal_value / (1 + wacc) ** n

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
                     nwc_pct_revenue, tax_rate, wacc_range: list, growth_range: list,
                     net_debt: float, shares_outstanding: float) -> pd.DataFrame:
    """Tableau de sensibilité valeur par action, WACC (lignes) x croissance terminale (colonnes)."""
    table = pd.DataFrame(index=wacc_range, columns=growth_range, dtype=float)
    for w in wacc_range:
        for g in growth_range:
            if g >= w:
                table.loc[w, g] = np.nan
                continue
            res = compute_dcf(base_revenue, revenue_growth_rates, ebitda_margin, da_pct_revenue,
                               capex_pct_revenue, nwc_pct_revenue, tax_rate, w,
                               terminal_method="growth", terminal_growth=g,
                               net_debt=net_debt, shares_outstanding=shares_outstanding)
            table.loc[w, g] = res["value_per_share"]
    return table


# ================================================ MULTIPLES (comps / transactions) ===
def implied_valuation_from_multiples(multiples: list, metric_value: float,
                                      net_debt: float, shares_outstanding: float) -> dict:
    """
    Applique une distribution de multiples (comparables boursiers ou transactions précédentes)
    à un indicateur de la cible (EBITDA ou Revenue) pour obtenir une fourchette de valorisation.
    Bande basse/haute = 25e/75e percentile (moins sensible aux valeurs extrêmes que min/max).
    """
    if not multiples:
        return None
    arr = np.array(multiples, dtype=float)
    stats = {
        "low": float(np.percentile(arr, 25)),
        "median": float(np.median(arr)),
        "high": float(np.percentile(arr, 75)),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "n": len(arr),
    }
    results = {}
    for label in ["low", "median", "high"]:
        multiple = stats[label]
        ev = multiple * metric_value
        equity_value = ev - net_debt
        per_share = equity_value / shares_outstanding if shares_outstanding else None
        results[label] = {"multiple": multiple, "ev": ev, "equity_value": equity_value, "per_share": per_share}
    return {"stats": stats, "valuation": results}


# ========================================================= SYNERGIES =====
def compute_synergies_npv(annual_pretax_synergies: float, phase_in: list, tax_rate: float,
                           discount_rate: float, terminal_growth: float = 0.0) -> dict:
    """
    VAN des synergies après impôt : montée en puissance explicite (phase_in, ex [0.3, 0.7, 1.0]),
    puis perpétuité du montant en régime de croisière (dernier taux de phase_in).
    """
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

    return {
        "rows": rows,
        "pv_explicit_sum": pv_sum,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "npv": pv_sum + pv_terminal_value,
    }
