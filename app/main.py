from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.upload import router as upload_router
from app.api.routes.reports import router as reports_router
from app.api.routes.dataset import router as dataset_router

from app.core.logging import setup_logging

tags_metadata = [
    {"name": "upload", "description": "Endpoints de entrada e validação de dados (upload)."},
    {"name": "reports", "description": "Relatórios analíticos (vendas, finanças, produtos, região, clientes)."},
    {"name": "dataset", "description": "Status e informações do dataset carregado em memória."},
    {"name": "default", "description": "Endpoints básicos (ex: health check)."},
]

app = FastAPI(
    title="Hanami Analytics API",
    version="0.1.0",
    description="API para processamento de CSV/XLSX e geração de relatórios analíticos.",
    openapi_tags=tags_metadata,
)

setup_logging()


@app.get(
    "/",
    summary="Root",
    description="Endpoint raiz com links úteis para documentação e health check.",
)
def root():
    return {
        "message": "Hanami Analytics API está no ar.",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


app.include_router(upload_router)
app.include_router(reports_router)
app.include_router(dataset_router)


