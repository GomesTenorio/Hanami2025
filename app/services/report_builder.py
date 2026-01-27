from __future__ import annotations

from datetime import datetime
import app.core.storage as storage

from app.services.calculations import calculate_sales_metrics, calculate_financial_metrics
from app.services.product_analysis import product_analysis
from app.services.demographics_region import customer_profile_as_object, regional_metrics


def build_report_dict() -> dict:
    """
    Montar um relatório consolidado em dict (pronto para JSON/PDF),
    usando o dataset carregado em memória.
    """
    if storage.CURRENT_DATASET is None:
        raise ValueError("Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df
    now = datetime.utcnow().isoformat()

    sales = calculate_sales_metrics(df)
    finance = calculate_financial_metrics(df)

    # regional_metrics retorna lista; converte para objeto por região
    regional_list = regional_metrics(df)
    regional_obj = {
        item["regiao"]: {
            "total_vendas": float(item["total_vendas"]),
            "numero_transacoes": int(item["numero_transacoes"]),
            "media_por_transacao": float(item["media_por_transacao"]),
        }
        for item in regional_list
    }

    products = product_analysis(df, sort_by="total_arrecadado", order="desc")[:20]  # top 20

    customers = customer_profile_as_object(df)

    return {
        "generated_at": now,
        "arquivo_original": storage.CURRENT_DATASET.filename,
        "linhas_processadas": int(len(df)),
        "sales_summary": sales,
        "financial_metrics": finance,
        "regional_performance": regional_obj,
        "product_analysis_top20": products,
        "customer_profile": customers,
    }
