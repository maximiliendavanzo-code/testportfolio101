"""
Export des résultats d'analyse de portefeuille en Excel et en PDF
(avec graphiques intégrés).
"""
from io import BytesIO
from datetime import date

import pandas as pd
from fpdf import FPDF, XPos, YPos


def build_excel_report(result: dict, target_currency: str, start_date: date, end_date: date,
                        freq_label: str, chart_data: pd.DataFrame) -> bytes:
    """Génère un classeur Excel avec 3 feuilles : Résumé, Performance, Corrélation."""
    metrics_rows = [
        ("Rendement total", f"{result['total_return']*100:.2f}%"),
        ("CAGR (annualisé)", f"{result['cagr']*100:.2f}%"),
        ("Volatilité annualisée", f"{result['volatility_annualized']*100:.2f}%"),
        ("Ratio de Sharpe", f"{result['sharpe']:.2f}"),
        ("Max drawdown", f"{result['max_drawdown']*100:.2f}%"),
        ("VaR historique", f"{result['var_historical']*100:.2f}%"),
        ("Expected Shortfall historique", f"{result['es_historical']*100:.2f}%"),
        ("VaR paramétrique", f"{result['var_parametric']*100:.2f}%"),
        ("Expected Shortfall paramétrique", f"{result['es_parametric']*100:.2f}%"),
        ("Devise", target_currency),
        ("Période", f"{start_date} → {end_date}"),
        ("Fréquence des données", freq_label),
        ("Nombre de périodes", result["n_periods"]),
    ]
    metrics_df = pd.DataFrame(metrics_rows, columns=["Indicateur", "Valeur"])

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        metrics_df.to_excel(writer, sheet_name="Résumé", index=False)
        chart_data.to_excel(writer, sheet_name="Performance")
        result["correlation"].to_excel(writer, sheet_name="Corrélation")
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf_report(result: dict, target_currency: str, start_date: date, end_date: date,
                      freq_label: str, tickers: list, performance_png: bytes,
                      correlation_png: bytes) -> bytes:
    """Génère un rapport PDF avec les indicateurs clés et les deux graphiques principaux."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Rapport d'analyse de portefeuille", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 6, f"Actifs : {', '.join(tickers)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Periode : {start_date} au {end_date} ({freq_label.lower()}), devise : {target_currency}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Indicateurs de performance et de risque", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10.5)

    rows = [
        ("Rendement total", f"{result['total_return']*100:.2f}%"),
        ("CAGR (annualisé)", f"{result['cagr']*100:.2f}%"),
        ("Volatilité annualisée", f"{result['volatility_annualized']*100:.2f}%"),
        ("Ratio de Sharpe", f"{result['sharpe']:.2f}"),
        ("Max drawdown", f"{result['max_drawdown']*100:.2f}%"),
        (f"VaR historique", f"{result['var_historical']*100:.2f}%"),
        (f"Expected Shortfall historique", f"{result['es_historical']*100:.2f}%"),
        (f"VaR paramétrique", f"{result['var_parametric']*100:.2f}%"),
    ]
    for label, value in rows:
        pdf.cell(90, 7, label)
        pdf.cell(0, 7, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, f"Performance cumulée (base 100, {target_currency})", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    _add_image_from_bytes(pdf, performance_png, width=190)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Matrice de corrélation", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    _add_image_from_bytes(pdf, correlation_png, width=140)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.ln(6)
    pdf.multi_cell(0, 5, "Performances passées, ne préjugent pas des performances futures. "
                          "Ceci n'est pas un conseil en investissement.")

    return bytes(pdf.output())


def _add_image_from_bytes(pdf: FPDF, img_bytes: bytes, width: float) -> None:
    """Insère une image PNG (en mémoire) dans le PDF sans passer par un fichier temporaire."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(img_bytes)
        tmp_path = tmp.name
    try:
        pdf.image(tmp_path, x=10, w=width)
    finally:
        os.unlink(tmp_path)
