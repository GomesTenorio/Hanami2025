from __future__ import annotations

from fastapi import APIRouter
import app.core.storage as storage

from app.docs.examples import DATASET_STATUS_EXAMPLE_LOADED

router = APIRouter(tags=["dataset"])


@router.get(
    "/dataset/status",
    summary="Status do dataset carregado",
    description="Indica se existe dataset carregado em memória e retorna metadados (arquivo, colunas, linhas).",
    responses={
        200: {"content": {"application/json": {"example": DATASET_STATUS_EXAMPLE_LOADED}}},
    },
)
def dataset_status():
    if storage.CURRENT_DATASET is None:
        return {
            "loaded": False,
            "message": "Nenhum dataset carregado. Faça upload em /upload.",
        }

    ds = storage.CURRENT_DATASET
    return {
        "loaded": True,
        "arquivo_original": ds.filename,
        "uploaded_at": ds.uploaded_at.isoformat(),
        "linhas_processadas": int(len(ds.df)),
        "colunas": list(ds.df.columns),
    }
