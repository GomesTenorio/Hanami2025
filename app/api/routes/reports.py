from __future__ import annotations

import json
from io import BytesIO

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger

import app.core.storage as storage

from app.services.calculations import calculate_sales_metrics, calculate_financial_metrics
from app.services.product_analysis import product_analysis
from app.services.demographics_region import regional_metrics, customer_profile_as_object
from app.services.report_builder import build_report_dict
from app.services.report_export import export_report_pdf_bytes, version_export_file

from app.docs.examples import (
    SALES_SUMMARY_EXAMPLE,
    FINANCIAL_METRICS_EXAMPLE,
    PRODUCT_ANALYSIS_EXAMPLE,
    REGIONAL_PERFORMANCE_EXAMPLE,
    CUSTOMER_PROFILE_EXAMPLE,
    DOWNLOAD_ERROR_EXAMPLE,
)

router = APIRouter(tags=["reports"])


@router.get(
    "/reports/sales-summary",
    summary="Resumo de vendas",
    description="Retorna métricas consolidadas de vendas: total de vendas, número de transações e média por transação.",
    responses={
        200: {"content": {"application/json": {"example": SALES_SUMMARY_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
    },
)
def sales_summary():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")
    return calculate_sales_metrics(storage.CURRENT_DATASET.df)


@router.get(
    "/reports/financial-metrics",
    summary="Métricas financeiras",
    description=(
        "Retorna receita líquida, lucro bruto e custo total estimado. "
        "Obs: custo_total = receita_liquida - lucro_bruto (estimado via margem_lucro)."
    ),
    responses={
        200: {"content": {"application/json": {"example": FINANCIAL_METRICS_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
    },
)
def financial_metrics():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")
    return calculate_financial_metrics(storage.CURRENT_DATASET.df)


@router.get(
    "/reports/product-analysis",
    summary="Análise de produtos",
    description=(
        "Retorna uma lista de produtos com quantidade vendida e total arrecadado. "
        "Permite ordenação via query params."
    ),
    responses={
        200: {"content": {"application/json": {"example": PRODUCT_ANALYSIS_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
        422: {"description": "Arquivo inválido (ex: colunas ausentes)."},
    },
)
def report_product_analysis(
    sort_by: str = Query(
        default="total_arrecadado",
        description="Campo de ordenação",
        enum=["quantidade", "total_arrecadado", "nome"],
    ),
    order: str = Query(
        default="desc",
        description="Direção da ordenação",
        enum=["asc", "desc"],
    ),
):
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    try:
        result = product_analysis(df, sort_by=sort_by, order=order)
        logger.info(f"Product analysis gerado. sort_by={sort_by} order={order} itens={len(result)}")
        return result
    except ValueError as e:
        logger.error(f"Product analysis falhou. erro={str(e)}")
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/reports/regional-performance",
    summary="Performance por região",
    description="Retorna um JSON com cada região como chave e suas métricas (vendas, transações e média) como valor.",
    responses={
        200: {"content": {"application/json": {"example": REGIONAL_PERFORMANCE_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
        422: {"description": "Arquivo inválido (ex: colunas ausentes)."},
    },
)
def regional_performance():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    try:
        metrics_list = regional_metrics(df)
        result = {
            item["regiao"]: {
                "total_vendas": float(item["total_vendas"]),
                "numero_transacoes": int(item["numero_transacoes"]),
                "media_por_transacao": float(item["media_por_transacao"]),
            }
            for item in metrics_list
        }

        logger.info(f"Regional performance gerado. regioes={len(result)}")
        return result
    except ValueError as e:
        logger.error(f"Regional performance falhou. erro={str(e)}")
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/reports/customer-profile",
    summary="Perfil de clientes",
    description="Distribuições demográficas: gênero, faixa etária e cidade. Retorna contagem e percentual.",
    responses={
        200: {"content": {"application/json": {"example": CUSTOMER_PROFILE_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
        422: {"description": "Arquivo inválido (ex: colunas ausentes)."},
    },
)
def customer_profile():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    try:
        profile = customer_profile_as_object(df)
        logger.info("Customer profile gerado.")
        return profile
    except ValueError as e:
        logger.error(f"Customer profile falhou. erro={str(e)}")
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/reports/download",
    summary="Download de relatório (JSON/PDF)",
    description="Gera e retorna um arquivo report.json ou report.pdf para download. O PDF inclui tabela e gráfico.",
    responses={
        200: {"description": "Arquivo gerado com sucesso (download)."},
        400: {"content": {"application/json": {"example": DOWNLOAD_ERROR_EXAMPLE}}},
    },
)
def download_report(
    format: str = Query(
        default="json",
        description="Formato do arquivo para download",
        enum=["json", "pdf"],
    )
):
    fmt = (format or "").strip().lower()

    if fmt not in ["json", "pdf"]:
        raise HTTPException(status_code=400, detail="Formato inválido. Use format=json ou format=pdf.")

    if fmt == "json":
        report_dict = build_report_dict()
        content = json.dumps(report_dict, ensure_ascii=False, indent=2).encode("utf-8")

        version_export_file(content, "json")

        return StreamingResponse(
            BytesIO(content),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=report.json"},
        )

    pdf_bytes = export_report_pdf_bytes()
    version_export_file(pdf_bytes, "pdf")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report.pdf"},
    )
