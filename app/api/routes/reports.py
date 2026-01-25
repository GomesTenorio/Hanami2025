from fastapi import Query
from loguru import logger
import app.core.storage as storage
from fastapi import APIRouter, HTTPException

from app.services.calculations import calculate_sales_metrics, calculate_financial_metrics
from app.services.product_analysis import product_analysis
from app.services.demographics_region import regional_metrics, customer_profile_as_object

router = APIRouter(tags=["reports"])


@router.get("/reports/sales-summary")
def sales_summary():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")
    return calculate_sales_metrics(storage.CURRENT_DATASET.df)


@router.get("/reports/financial-metrics")
def financial_metrics():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")
    return calculate_financial_metrics(storage.CURRENT_DATASET.df)


@router.get("/reports/product-analysis")
def report_product_analysis(
    sort_by: str = Query(default="total_arrecadado", description="quantidade | total_arrecadado | nome"),
    order: str = Query(default="desc", description="asc | desc"),
):
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    try:
        result = product_analysis(df, sort_by=sort_by, order=order)
        logger.info(f"Product analysis gerado. sort_by={sort_by} order={order} itens={len(result)}")
        return result
    except ValueError as e:
        # erro claro se faltar colunas necessárias
        logger.error(f"Product analysis falhou. erro={str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    
@router.get("/reports/regional-performance")
def regional_performance():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")

    df = storage.CURRENT_DATASET.df

    try:
        metrics_list = regional_metrics(df)

        # Formato pedido: cada região como chave
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


@router.get("/reports/customer-profile")
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

