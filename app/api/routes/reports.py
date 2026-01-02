from fastapi import APIRouter, HTTPException
import app.core.storage as storage

from app.services.calculations import calculate_sales_metrics, calculate_financial_metrics

router = APIRouter(tags=["reports"])


@router.get("/reports/financial-metrics")
def financial_metrics():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")
    return calculate_financial_metrics(storage.CURRENT_DATASET.df)


@router.get("/reports/sales-summary")
def sales_summary():
    if storage.CURRENT_DATASET is None:
        raise HTTPException(status_code=400, detail="Nenhum dataset carregado. Faça upload em /upload.")
    return calculate_sales_metrics(storage.CURRENT_DATASET.df)

