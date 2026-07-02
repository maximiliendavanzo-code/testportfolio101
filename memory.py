"""
Mémorise automatiquement la dernière configuration de portefeuille utilisée,
pour la retrouver au prochain lancement de l'app — sans compte utilisateur.

Limite à connaître : ce fichier est partagé par tout le monde qui utilise
l'app (pas de notion de compte), et peut être réinitialisé si l'app est
redéployée sur Streamlit Community Cloud. Convient très bien pour un usage
personnel ou entre proches.
"""
import json
import os

LAST_PORTFOLIO_FILE = "last_portfolio.json"


def load_last_portfolio() -> dict:
    if not os.path.exists(LAST_PORTFOLIO_FILE):
        return {}
    try:
        with open(LAST_PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_last_portfolio(data: dict) -> None:
    try:
        with open(LAST_PORTFOLIO_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass  # on n'interrompt jamais l'app si l'écriture échoue
