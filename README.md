# Analyseur de portefeuille

Webapp Python (Streamlit) : entrez des tickers, une période, une devise et
des pondérations, elle va chercher les données réelles sur Yahoo Finance et
calcule automatiquement performance, corrélation, volatilité, VaR
(historique et paramétrique) et Expected Shortfall.

## Fonctionnalités

- **Finance101** : portail avec 3 outils — Portfolio101 (fonctionnel), CIB101 (à venir), **M&A101** (fonctionnel).
- **M&A101** : suite de valorisation complète, dans l'esprit d'un vrai modèle
  de deal (DCF mid-year, BFR en jours, synergies de revenus, structuration
  d'offre, financement, accretion/dilution, capacité d'endettement) —
  cible et acquéreur, tickers réels ou saisie manuelle. 8 onglets : DCF,
  Comparables, Transactions, Synergies, Football Field, Offre & Prime,
  Financement & BPA, Capacité d'endettement.
- **Page d'accueil** : logo, présentation du site, bouton "Commencer" vers l'outil d'analyse.
- **Sélecteur de langue** (français / anglais) en haut à droite, sur toutes les pages.
- **Logo Portfolio101** : icône d'onglet et en-tête personnalisés (SVG, net à toute résolution).
- **Sélection de tickers facilitée** : liste de valeurs populaires (tech US,
  CAC 40, ETF, crypto) + possibilité de taper n'importe quel symbole Yahoo
  Finance personnalisé.
- **Conversion de devise** : choisissez une devise cible (EUR, USD, GBP,
  CHF, JPY, CAD) — chaque actif est automatiquement converti depuis sa
  devise native via les taux de change historiques.
- **Pondérations strictes** : le bouton "Analyser" reste désactivé tant que
  le total des pondérations n'est pas exactement 100%. Un bouton "Répartir
  équitablement" remet tout à égalité en un clic.
- **Tous les indicateurs sont expliqués** : passez la souris sur le "?" à
  côté de chaque résultat pour en comprendre le sens.
- **Mémorisation automatique** : le dernier portefeuille analysé est
  retrouvé au prochain lancement, sans compte à créer.
- **Export des résultats** : Excel (données + indicateurs), image PNG du
  graphique de performance, et rapport PDF complet.

## Installation

Nécessite Python 3.9+.

```bash
# 1. (recommandé) créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate      # sous Windows : venv\Scripts\activate

# 2. installer les dépendances
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run app.py
```

Cela ouvre automatiquement l'application dans votre navigateur, en local (une
adresse du type `http://localhost:8501`). Tant que le terminal reste ouvert,
l'application tourne.

## Utilisation

1. Dans la barre latérale, sélectionnez des tickers dans la liste ou tapez-en
   un personnalisé (symbole Yahoo Finance, ex: `MC.PA` pour LVMH).
2. Choisissez la devise cible du portefeuille.
3. Choisissez la période et la fréquence des données.
4. Ajustez les pondérations — le total doit être exactement 100% (indiqué en
   vert) pour pouvoir lancer l'analyse. Utilisez "Répartir équitablement"
   pour repartir à zéro rapidement.
5. Réglez le taux sans risque et le niveau de confiance pour la VaR/ES.
6. Cliquez sur "Analyser le portefeuille".
7. Téléchargez les résultats en Excel, PNG ou PDF depuis le bas de la page.

## Mettre en ligne (optionnel — pour avoir une vraie URL publique)

Le moyen le plus simple et gratuit est **Streamlit Community Cloud** :

1. Créez un dépôt GitHub avec tous les fichiers `.py`, `requirements.txt`,
   le dossier `assets/` et le dossier `.streamlit/` (`app.py`, `finance.py`,
   `currency.py`, `tickers.py`, `memory.py`, `export.py`,
   `requirements.txt`, `assets/favicon.png`, `assets/logo_wordmark.png`,
   `.streamlit/config.toml`).
2. Allez sur [streamlit.io/cloud](https://streamlit.io/cloud), connectez votre
   compte GitHub et sélectionnez le dépôt.
3. Streamlit déploie automatiquement l'app et vous donne une URL publique
   (ex: `https://votre-app.streamlit.app`), accessible depuis n'importe quel
   navigateur, sans que vous ayez besoin de laisser votre ordinateur allumé.

## Notes

- Les données viennent de Yahoo Finance via la librairie `yfinance` ; elles
  sont mises en cache 1h pour limiter les appels réseau.
- Le portefeuille est simulé en *buy-and-hold* (pondérations fixées au
  départ, sans rééquilibrage automatique).
- Le "dernier portefeuille" est mémorisé dans un fichier partagé par toute
  personne utilisant l'app (pas de compte = pas de séparation par
  utilisateur), et peut être réinitialisé si l'app est redéployée sur
  Streamlit Community Cloud.
- Ceci est un outil d'analyse personnel, pas un conseil en investissement.
