from __future__ import annotations

from io import BytesIO
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from app.services.report_builder import build_report_dict


def _make_region_bar_chart(regional_performance: dict) -> BytesIO:
    """
    Gera um gráfico de barras (vendas por região) e devolve em BytesIO (PNG).
    """
    regions = list(regional_performance.keys())
    values = [float(regional_performance[r]["total_vendas"]) for r in regions]

    buf = BytesIO()

    plt.figure()
    plt.bar(regions, values)
    plt.title("Vendas por Região")
    plt.xlabel("Região")
    plt.ylabel("Total de Vendas")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(buf, format="png", dpi=150)
    plt.close()

    buf.seek(0)
    return buf


def export_report_pdf_bytes() -> bytes:
    """
    Cria um PDF com:
    - título e metadados
    - tabela (vendas por região)
    - gráfico (barras de vendas por região)
    """
    report = build_report_dict()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Hanami Report")

    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph("Relatório Analítico", styles["Title"]))
    story.append(Spacer(1, 0.4 * cm))

    # Metadados
    meta = (
        f"<b>Gerado em:</b> {report['generated_at']}<br/>"
        f"<b>Arquivo:</b> {report['arquivo_original']}<br/>"
        f"<b>Linhas processadas:</b> {report['linhas_processadas']}"
    )
    story.append(Paragraph(meta, styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Métricas principais
    sales = report["sales_summary"]
    finance = report["financial_metrics"]

    story.append(Paragraph("Métricas principais", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))

    story.append(
        Paragraph(
            f"Total de vendas: {float(sales['total_vendas']):.2f}<br/>"
            f"Número de transações: {int(sales['numero_transacoes'])}<br/>"
            f"Média por transação: {float(sales['media_por_transacao']):.2f}<br/>"
            f"Receita líquida: {float(finance['receita_liquida']):.2f}<br/>"
            f"Lucro bruto: {float(finance['lucro_bruto']):.2f}<br/>"
            f"Custo total: {float(finance['custo_total']):.2f}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.6 * cm))

    # Tabela: vendas por região
    story.append(Paragraph("Vendas por região", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))

    regional = report["regional_performance"]
    if not regional:
        raise ValueError(
            "Sem dados regionais para gerar o PDF. Verifique se a coluna 'regiao' existe e se há linhas válidas."
        )

    data = [["Região", "Total de Vendas", "Transações", "Média/Transação"]]
    for regiao, m in regional.items():
        data.append(
            [
                str(regiao),
                f"{float(m['total_vendas']):.2f}",
                str(int(m["numero_transacoes"])),
                f"{float(m['media_por_transacao']):.2f}",
            ]
        )

    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))

    # Gráfico: barras por região
    story.append(Paragraph("Gráfico: vendas por região", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))

    chart_buf = _make_region_bar_chart(regional)
    chart_img = Image(chart_buf, width=16 * cm, height=9 * cm)
    story.append(chart_img)

    # Build
    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def version_export_file(content: bytes, ext: str) -> Path:
    """
    Versiona artefatos de exportação em /exports com timestamp.
    Retorna o path salvo.
    """
    exports_dir = Path("exports")
    exports_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = exports_dir / f"report_{ts}.{ext}"
    path.write_bytes(content)
    return path
