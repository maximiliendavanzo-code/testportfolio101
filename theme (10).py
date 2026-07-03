"""
Thème "verre optique" pour Finance101 : dégradés de fond tintés par outil, cartes
translucides avec effet de flou (glassmorphism), jauges en anneau pour les indicateurs
clés. Police : Outfit (titres et contenu).
"""
import re
import streamlit as st

INK = "#12141c"
TEXT_SECONDARY = "#4b4f5e"

PURPLE = "#6B2FBF"
ACCENTS = {"finance": PURPLE, "portfolio": PURPLE, "ma": PURPLE, "cib": PURPLE}


def _html(body: str) -> None:
    """
    st.markdown(unsafe_allow_html=True) mais en retirant d'abord toute indentation et toute
    ligne vide : sinon Streamlit (Markdown GitHub-flavored) peut interpréter une ligne
    indentée, ou une ligne blanche au milieu d'un bloc HTML/CSS, comme la fin du bloc HTML
    brut — et afficher la suite telle quelle au lieu de la rendre.
    """
    compact = re.sub(r"\n\s*", "", body).strip()
    st.markdown(compact, unsafe_allow_html=True)


def _hex_to_rgb(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


def inject_glass_theme(accent_key: str) -> None:
    """Applique le thème verre optique, tinté par la couleur de l'outil actif."""
    accent = ACCENTS.get(accent_key, ACCENTS["finance"])
    accent_rgb = _hex_to_rgb(accent)

    _html(f"""
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

    /* formes flottantes décoratives : purement visuelles, jamais interactives */
    .bg-shape {{
        position: fixed;
        filter: blur(60px);
        opacity: 0.4;
        pointer-events: none !important;
        z-index: 0;
    }}
    .bg-shape-1 {{
        width: 460px; height: 420px; top: -140px; left: -100px;
        background: rgba({accent_rgb},0.55);
        border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
        animation: bgFloat1 24s ease-in-out infinite;
    }}
    .bg-shape-2 {{
        width: 360px; height: 320px; bottom: -100px; right: -80px;
        background: rgba({accent_rgb},0.4);
        border-radius: 40% 60% 70% 30% / 50% 60% 40% 50%;
        animation: bgFloat2 28s ease-in-out infinite;
    }}
    .bg-shape-3 {{
        width: 260px; height: 240px; top: 45%; right: 12%;
        background: rgba({accent_rgb},0.3);
        border-radius: 55% 45% 65% 35% / 40% 55% 45% 60%;
        animation: bgFloat3 20s ease-in-out infinite;
    }}
    @keyframes bgFloat1 {{
        0%, 100% {{ transform: translate(0,0) scale(1) rotate(0deg); }}
        50% {{ transform: translate(60px,50px) scale(1.12) rotate(15deg); }}
    }}
    @keyframes bgFloat2 {{
        0%, 100% {{ transform: translate(0,0) scale(1) rotate(0deg); }}
        50% {{ transform: translate(-50px,-40px) scale(1.1) rotate(-12deg); }}
    }}
    @keyframes bgFloat3 {{
        0%, 100% {{ transform: translate(0,0) scale(1) rotate(0deg); }}
        50% {{ transform: translate(-40px,50px) scale(0.9) rotate(10deg); }}
    }}
    [data-testid="stAppViewContainer"] > .main {{ position: relative; z-index: 1; }}

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
        background: rgba(255,255,255,0.32);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 16px;
        transition: background 0.25s ease, border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
    }}
    div[data-testid="stExpander"]:hover {{
        background: rgba({accent_rgb},0.10);
        border-color: rgba({accent_rgb},0.35);
        transform: scale(1.01);
        box-shadow: 0 8px 24px rgba({accent_rgb},0.15);
    }}

    div[data-testid="stMetric"] {{
        transition: background 0.25s ease, border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        background: rgba({accent_rgb},0.12);
        border-color: rgba({accent_rgb},0.35);
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba({accent_rgb},0.15);
    }}

    .ring-panel:hover {{
        background: rgba({accent_rgb},0.14) !important;
        border-color: rgba({accent_rgb},0.4) !important;
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba({accent_rgb},0.18);
    }}

    .stButton > button, .stDownloadButton > button {{
        background: {accent} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 20px rgba({accent_rgb},0.4);
        transition: filter 0.15s, transform 0.15s;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        filter: brightness(1.08);
        transform: scale(1.03);
    }}
    .stButton > button p, .stDownloadButton > button p {{ color: white !important; }}

    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div, div[data-testid="stDateInput"] input {{
        background: rgba(255,255,255,0.6) !important;
        border: none !important;
        border-radius: 10px !important;
    }}

    input[type="range"] {{ accent-color: {accent} !important; }}

    /* sélecteur de langue en verre */
    div[class*="st-key-lang_selector"] [data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.55) !important;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.7) !important;
        border-radius: 999px !important;
        box-shadow: 0 6px 18px rgba({accent_rgb},0.12);
    }}

    .glass-card {{
        padding: 26px;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        background: linear-gradient(160deg, rgba(255,255,255,0.32), rgba(255,255,255,0.14));
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        height: 100%;
        transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }}
    .glass-card:hover {{
        background: linear-gradient(160deg, rgba({accent_rgb},0.22), rgba({accent_rgb},0.10));
        border-color: rgba({accent_rgb},0.4);
        transform: scale(1.02);
        box-shadow: 0 12px 36px rgba({accent_rgb},0.22);
    }}
    </style>
    """)


def render_bg_shapes() -> None:
    """Insère les formes flottantes décoratives (à appeler une fois par page, après inject_glass_theme)."""
    _html("""
    <div class="bg-shape bg-shape-1"></div>
    <div class="bg-shape bg-shape-2"></div>
    <div class="bg-shape bg-shape-3"></div>
    """)


ICONS = {
    "portfolio": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "cib": '<path d="M3 21h18"/><path d="M5 21V10"/><path d="M19 21V10"/><path d="M2 10l10-6 10 6"/><path d="M9 21v-6"/><path d="M15 21v-6"/>',
    "ma": '<path d="M8 3L3 8l5 5"/><path d="M3 8h11a4 4 0 0 1 4 4v1"/><path d="M16 21l5-5-5-5"/><path d="M21 16H10a4 4 0 0 1-4-4v-1"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 9l-5 5-3-3-4 4"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "shield": '<path d="M12 3l8 4v5c0 5-3.4 8.4-8 9-4.6-.6-8-4-8-9V7l8-4z"/><path d="M9 12l2 2 4-4"/>',
}


def render_icon(name: str, color: str, size: int = 24) -> str:
    inner = ICONS.get(name, "")
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')


def render_tool_card(name: str, suffix: str, accent_key: str, description: str,
                      icon: str = None, tags: list = None, badge: str = None) -> None:
    """Carte en verre enrichie : icône, titre + suffixe coloré, description, tags, badge éventuel."""
    accent = ACCENTS.get(accent_key, ACCENTS["finance"])
    accent_rgb = _hex_to_rgb(accent)

    icon_html = ""
    if icon:
        icon_html = (
            f'<div style="width:44px; height:44px; border-radius:12px; background:rgba({accent_rgb},0.12); '
            f'display:flex; align-items:center; justify-content:center;">{render_icon(icon, accent, 22)}</div>'
        )

    tags_html = ""
    if tags:
        pills = "".join(
            f'<span style="font-size:12px; font-weight:600; color:{accent}; background:rgba({accent_rgb},0.10); '
            f'border:1px solid rgba({accent_rgb},0.25); border-radius:999px; padding:5px 12px;">{tag}</span>'
            for tag in tags
        )
        tags_html = f'<div style="display:flex; flex-wrap:wrap; gap:8px;">{pills}</div>'

    badge_html = (
        f'<div style="align-self:flex-start; color:{accent}; font-weight:700; font-size:12px; '
        f'letter-spacing:0.03em; border:1px solid rgba({accent_rgb},0.4); padding:10px 18px; '
        f'border-radius:12px;">{badge}</div>'
        if badge else ""
    )

    _html(f"""
    <div class="glass-card">
      {icon_html}
      <div>
        <div style="font-family:'Outfit',sans-serif; font-weight:700; font-size:20px; color:{INK};">
          {name}<span style="color:{accent};">{suffix}</span>
        </div>
        <div style="width:32px; height:3px; background:{accent}; border-radius:2px; margin-top:4px;"></div>
      </div>
      <div style="font-size:14px; color:{TEXT_SECONDARY}; line-height:1.5; flex:1;">{description}</div>
      {tags_html}
      {badge_html}
    </div>
    """)


def render_ring_metric(value_str: str, value: float, vmin: float, vmax: float, label: str,
                        accent_key: str, help_text: str = "") -> None:
    """Jauge en anneau (glass panel) pour un indicateur clé — valeur normalisée entre vmin et vmax pour l'arc."""
    accent = ACCENTS.get(accent_key, ACCENTS["finance"])
    accent_rgb = _hex_to_rgb(accent)
    pct = max(0.0, min(1.0, (value - vmin) / (vmax - vmin))) if vmax > vmin else 0.0
    deg = round(pct * 360)
    title_attr = help_text.replace('"', "&quot;") if help_text else ""
    _html(f"""
    <div title="{title_attr}" class="ring-panel" style="display:flex; align-items:center; gap:14px; background:rgba(255,255,255,0.32);
                backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
                border:1px solid rgba(255,255,255,0.5); border-radius:18px; padding:14px 18px;
                height:100%; cursor:help; transition: background 0.25s ease, border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;">
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
    """)


def render_stats_bar(items: list) -> None:
    """Bandeau de chiffres clés. items: liste de tuples (icon_name, label, caption)."""
    blocks = "".join(f"""
        <div style="display:flex; align-items:center; gap:12px;">
          <div style="width:44px; height:44px; border-radius:50%; background:rgba(255,255,255,0.8);
                      border:1px solid rgba(255,255,255,0.7); display:flex; align-items:center;
                      justify-content:center; flex-shrink:0;">
            {render_icon(icon_name, PURPLE, 20)}
          </div>
          <div>
            <div style="font-weight:700; font-size:15px; color:{INK};">{label}</div>
            <div style="font-size:12px; color:{TEXT_SECONDARY};">{caption}</div>
          </div>
        </div>
        """ for icon_name, label, caption in items)
    _html(f'<div style="display:flex; gap:36px; flex-wrap:wrap; margin:8px 0 34px;">{blocks}</div>')


def render_hero_illustration(*args, **kwargs) -> None:
    """Illustration hero : image fournie (laptop + cartes flottantes), affichée telle quelle."""
    st.image("hero_illustration.png", use_container_width=True)


def render_how_it_works(title: str, steps: list) -> None:
    """steps : liste de tuples (titre, description), affichés en 3 étapes numérotées reliées par un trait."""
    accent_rgb = _hex_to_rgb(PURPLE)
    n = len(steps)
    items_html = "".join(f"""
        <div style="flex:1; position:relative; z-index:1; padding:0 18px; min-width:180px;">
          <div style="width:36px; height:36px; border-radius:50%; background:rgba({accent_rgb},0.14);
                      color:{PURPLE}; font-weight:800; display:flex; align-items:center; justify-content:center;
                      margin-bottom:10px;">{i+1}</div>
          <div style="font-weight:700; font-size:15px; color:{INK}; margin-bottom:4px;">{step_title}</div>
          <div style="font-size:13px; color:{TEXT_SECONDARY}; line-height:1.5;">{step_desc}</div>
        </div>
        """ for i, (step_title, step_desc) in enumerate(steps))
    _html(f"""
    <div style="text-align:center; font-weight:700; font-size:20px; color:{INK}; margin:12px 0 26px;">{title}</div>
    <div style="position:relative; display:flex; flex-wrap:wrap; justify-content:space-between; max-width:1000px; margin:0 auto;">
      <div style="position:absolute; top:18px; left:60px; right:60px; height:0;
                  border-top:2px dashed rgba({accent_rgb},0.3); z-index:0;"></div>
      {items_html}
    </div>
    """)


def render_footer(text: str) -> None:
    _html(f"""
    <div style="margin-top:50px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.6);
                text-align:center; font-size:12px; color:{TEXT_SECONDARY};">{text}</div>
    """)
