from __future__ import annotations

import json
from io import BytesIO

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger
from datetime import date

import app.core.storage as storage

from app.services.calculations import calculate_sales_metrics, calculate_financial_metrics
from app.services.product_analysis import product_analysis
from app.services.demographics_region import regional_metrics, customer_profile_as_object
from app.services.report_builder import build_report_dict
from app.services.report_export import export_report_pdf_bytes, version_export_file
from app.utils.filters import parse_yyyy_mm_dd, filter_by_date_range, filter_by_estado

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
    description=(
        "Retorna métricas consolidadas de vendas: total de vendas, número de transações e média por transação. "
        "Filtros opcionais: start_date e end_date (YYYY-MM-DD) para filtrar por período."
    ),
    responses={
        200: {"content": {"application/json": {"example": SALES_SUMMARY_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
        422: {"description": "Parâmetros inválidos (ex: data fora do formato YYYY-MM-DD)."},
    },
)
def sales_summary(
    start_date: str | None = Query(
        default=None,
        description="Data inicial (inclusiva) no formato YYYY-MM-DD",
        examples=["2023-01-01"],
    ),
    end_date: str | None = Query(
        default=None,
        description="Data final (inclusiva) no formato YYYY-MM-DD",
        examples=["2023-12-31"],
    ),
):
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    # Parse das datas
    try:
        s: date | None = parse_yyyy_mm_dd(start_date) if start_date else None
        e: date | None = parse_yyyy_mm_dd(end_date) if end_date else None
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    # Validação de intervalo
    if s and e and s > e:
        raise HTTPException(status_code=422, detail="Intervalo inválido: start_date não pode ser maior que end_date.")

    # Filtra por data_venda (assumindo que seu parser já converteu para datetime)
    filtered = filter_by_date_range(df, date_col="data_venda", start=s, end=e)

    return calculate_sales_metrics(filtered)


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
    description=(
        "Retorna um JSON com cada região como chave e suas métricas (vendas, transações e média) como valor. "
        "Filtro opcional: estado=UF para filtrar apenas clientes de um estado (ex: SP)."
    ),
    responses={
        200: {"content": {"application/json": {"example": REGIONAL_PERFORMANCE_EXAMPLE}}},
        400: {"description": "Nenhum dataset carregado. Faça upload em /upload."},
        422: {"description": "Arquivo inválido (ex: colunas ausentes)."},
    },
)
def regional_performance(
    estado: str | None = Query(
        default=None,
        description="Filtra por UF do cliente (ex: SP, RJ). Se não informado, retorna completo.",
        enum=["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],
    ),
):
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    try:
        filtered = filter_by_estado(df, estado)
        metrics_list = regional_metrics(filtered)

        result = {
            item["regiao"]: {
                "total_vendas": float(item["total_vendas"]),
                "numero_transacoes": int(item["numero_transacoes"]),
                "media_por_transacao": float(item["media_por_transacao"]),
            }
            for item in metrics_list
        }

        logger.info(f"Regional performance gerado. estado={estado or 'ALL'} regioes={len(result)}")
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
