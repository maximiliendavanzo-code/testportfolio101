"""
Fonctions de calcul financier pour l'analyseur de portefeuille.
Séparées de l'UI Streamlit pour être testables indépendamment.
"""
import numpy as np
import pandas as pd
from scipy import stats


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Rendements simples période sur période, à partir d'un DataFrame de prix (colonnes = tickers)."""
    return prices.pct_change().dropna(how="all")


def portfolio_value_series(prices: pd.DataFrame, weights: dict) -> pd.Series:
    """
    Valeur du portefeuille en buy-and-hold (pas de rééquilibrage), base 100 au départ.
    weights: dict {ticker: poids en fraction (0-1)}, doit sommer à ~1.
    """
    norm = prices / prices.iloc[0] * 100
    w = pd.Series(weights).reindex(prices.columns).fillna(0)
    return (norm * w).sum(axis=1)


def annualization_factor(freq: str) -> int:
    return {"daily": 252, "weekly": 52, "monthly": 12}.get(freq, 252)


def cagr(value_series: pd.Series, ann_factor: int) -> float:
    n_periods = len(value_series) - 1
    if n_periods <= 0:
        return 0.0
    total_growth = value_series.iloc[-1] / value_series.iloc[0]
    return total_growth ** (ann_factor / n_periods) - 1


def annualized_volatility(returns: pd.Series, ann_factor: int) -> float:
    return returns.std(ddof=1) * np.sqrt(ann_factor)


def sharpe_ratio(returns: pd.Series, ann_factor: int, risk_free_annual: float) -> float:
    vol = annualized_volatility(returns, ann_factor)
    if vol == 0:
        return 0.0
    excess = returns.mean() * ann_factor - risk_free_annual
    return excess / vol


def max_drawdown(value_series: pd.Series) -> float:
    running_max = value_series.cummax()
    drawdown = value_series / running_max - 1
    return drawdown.min()


def var_historical(returns: pd.Series, confidence: float) -> float:
    """VaR historique par période, retournée en valeur positive (perte)."""
    return -np.percentile(returns, (1 - confidence) * 100)


def expected_shortfall_historical(returns: pd.Series, confidence: float) -> float:
    var = var_historical(returns, confidence)
    tail = returns[returns <= -var]
    if len(tail) == 0:
        return var
    return -tail.mean()


def var_parametric(returns: pd.Series, confidence: float) -> float:
    z = stats.norm.ppf(confidence)
    return -(returns.mean() - z * returns.std(ddof=1))


def expected_shortfall_parametric(returns: pd.Series, confidence: float) -> float:
    z = stats.norm.ppf(confidence)
    phi_z = stats.norm.pdf(z)
    return -(returns.mean() - returns.std(ddof=1) * (phi_z / (1 - confidence)))


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def full_portfolio_analysis(prices: pd.DataFrame, weights: dict, freq: str,
                             risk_free_annual: float, confidence: float) -> dict:
    """Calcule l'ensemble des métriques pour un portefeuille donné."""
    ann_factor = annualization_factor(freq)
    asset_returns = compute_returns(prices)
    port_value = portfolio_value_series(prices, weights)
    port_returns = port_value.pct_change().dropna()

    return {
        "portfolio_value": port_value,
        "portfolio_returns": port_returns,
        "total_return": port_value.iloc[-1] / port_value.iloc[0] - 1,
        "cagr": cagr(port_value, ann_factor),
        "volatility_annualized": annualized_volatility(port_returns, ann_factor),
        "sharpe": sharpe_ratio(port_returns, ann_factor, risk_free_annual),
        "max_drawdown": max_drawdown(port_value),
        "var_historical": var_historical(port_returns, confidence),
        "es_historical": expected_shortfall_historical(port_returns, confidence),
        "var_parametric": var_parametric(port_returns, confidence),
        "es_parametric": expected_shortfall_parametric(port_returns, confidence),
        "correlation": correlation_matrix(asset_returns),
        "asset_returns": asset_returns,
        "n_periods": len(port_returns),
    }
