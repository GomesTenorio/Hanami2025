import os
from fastapi import FastAPI
from loguru import logger

from app.core.logging import setup_logging
from app.api.routes.upload import router as upload_router
from app.api.routes.reports import router as reports_router
from app.api.routes.dataset import router as dataset_router

setup_logging(os.getenv("LOG_LEVEL", "INFO"))
logger.info("Aplicação iniciada")

app = FastAPI(
    title="Hanami Analytics API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(upload_router)
app.include_router(reports_router)
app.include_router(dataset_router)

@app.get("/")
def root():
    return {
        "message": "Hanami Analytics API está no ar.",
        "docs": "/docs",
        "health": "/health",
        "upload": "/upload",
        "dataset_status": "/dataset/status",
    }

