"""
Thème "verre optique" pour Finance101 : dégradés de fond tintés par outil, cartes
translucides avec effet de flou (glassmorphism), jauges en anneau pour les indicateurs
clés. Police : Outfit (titres et contenu).
"""
import streamlit as st

INK = "#12141c"
TEXT_SECONDARY = "#4b4f5e"

PURPLE = "#6B2FBF"
ACCENTS = {"finance": PURPLE, "portfolio": PURPLE, "ma": PURPLE, "cib": PURPLE}


def _hex_to_rgb(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


def inject_glass_theme(accent_key: str) -> None:
    """Applique le thème verre optique, tinté par la couleur de l'outil actif."""
    accent = ACCENTS.get(accent_key, ACCENTS["finance"])
    accent_rgb = _hex_to_rgb(accent)

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, span, div, label {{
        font-family: 'Outfit', sans-serif;
    }}
    h1, h2, h3 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; }}

    .stApp {{
        background:
            radial-gradient(circle at 15% 10%, rgba({accent_rgb},0.14), transparent 45%),
            radial-gradient(circle at 85% 90%, rgba({accent_rgb},0.08), transparent 45%),
            linear-gradient(180deg,#f5f6fb,#eef0f7);
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(160deg, rgba(255,255,255,0.65), rgba(255,255,255,0.35));
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-right: 1px solid rgba(255,255,255,0.6);
    }}

    div[data-testid="stMetric"] {{
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 18px;
        padding: 14px 18px;
    }}

    div[data-testid="stExpander"], div[data-testid="stDataFrame"] {{
        background: rgba(255,255,255,0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 16px;
    }}

    .stButton > button, .stDownloadButton > button {{
        background: {accent} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 20px rgba({accent_rgb},0.4);
        transition: filter 0.15s;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{ filter: brightness(1.08); }}
    .stButton > button p, .stDownloadButton > button p {{ color: white !important; }}

    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div, div[data-testid="stDateInput"] input {{
        background: rgba(255,255,255,0.6) !important;
        border: none !important;
        border-radius: 10px !important;
    }}

    input[type="range"] {{ accent-color: {accent} !important; }}

    .glass-card {{
        padding: 26px;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        background: linear-gradient(160deg, rgba(255,255,255,0.65), rgba(255,255,255,0.35));
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.6);
        height: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_tool_card(name: str, suffix: str, accent_key: str, description: str, badge: str = None) -> None:
    """Carte en verre pour une entrée du portail Finance101 (nom, suffixe coloré, description)."""
    accent = ACCENTS.get(accent_key, ACCENTS["finance"])
    accent_rgb = _hex_to_rgb(accent)
    badge_html = (
        f'<div style="align-self:flex-start; color:{accent}; font-weight:700; font-size:12px; '
        f'letter-spacing:0.03em; border:1px solid rgba({accent_rgb},0.4); padding:10px 18px; '
        f'border-radius:12px;">{badge}</div>'
        if badge else ""
    )
    st.markdown(f"""
    <div class="glass-card" style="box-shadow:0 8px 32px rgba({accent_rgb},0.15);">
      <div>
        <div style="font-family:'Outfit',sans-serif; font-weight:700; font-size:20px; color:{INK};">
          {name}<span style="color:{accent};">{suffix}</span>
        </div>
        <div style="width:32px; height:3px; background:{accent}; border-radius:2px; margin-top:4px;"></div>
      </div>
      <div style="font-size:14px; color:{TEXT_SECONDARY}; line-height:1.5; flex:1;">{description}</div>
      {badge_html}
    </div>
    """, unsafe_allow_html=True)


def render_ring_metric(value_str: str, value: float, vmin: float, vmax: float, label: str,
                        accent_key: str, help_text: str = "") -> None:
    """Jauge en anneau (glass panel) pour un indicateur clé — valeur normalisée entre vmin et vmax pour l'arc."""
    accent = ACCENTS.get(accent_key, ACCENTS["finance"])
    accent_rgb = _hex_to_rgb(accent)
    pct = max(0.0, min(1.0, (value - vmin) / (vmax - vmin))) if vmax > vmin else 0.0
    deg = round(pct * 360)
    title_attr = help_text.replace('"', "&quot;") if help_text else ""
    st.markdown(f"""
    <div title="{title_attr}" style="display:flex; align-items:center; gap:14px; background:rgba(255,255,255,0.5);
                backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
                border:1px solid rgba(255,255,255,0.6); border-radius:18px; padding:14px 18px;
                height:100%; cursor:help;">
      <div style="width:80px; height:80px; border-radius:50%; flex-shrink:0;
                  background:conic-gradient({accent} 0deg {deg}deg, rgba({accent_rgb},0.14) {deg}deg 360deg);
                  display:flex; align-items:center; justify-content:center;">
        <div style="width:58px; height:58px; border-radius:50%; background:#fbfaff;
                    display:flex; align-items:center; justify-content:center;
                    font-family:'Outfit',sans-serif; font-weight:800; font-size:14px; color:{INK};">
          {value_str}
        </div>
      </div>
      <div style="font-size:11px; color:{TEXT_SECONDARY}; letter-spacing:0.02em;">{label}</div>
    </div>
    """, unsafe_allow_html=True)
