from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, HTTPException
from loguru import logger

import app.core.storage as storage
from app.services.parser import parse_upload_to_dataframe
from app.core.errors import DataValidationError

router = APIRouter(tags=["upload"])


@router.post(
    "/upload",
    summary="Upload do dataset",
    description=(
        "Recebe um arquivo CSV ou XLSX (multipart/form-data), valida e carrega em memória "
        "para uso pelos endpoints de relatórios."
    ),
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "sucesso",
                        "linhas_processadas": 10000,
                        "arquivo_original": "vendas_ficticias_10000_linhas.csv",
                    }
                }
            }
        },
        400: {"description": "Nenhum arquivo enviado."},
        422: {"description": "Arquivo inválido (ex: colunas faltando, tipos inválidos)."},
    },
)
async def upload_file(file: UploadFile = File(None)):
    if file is None:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    try:
        df = await parse_upload_to_dataframe(file)
        storage.set_dataset(df=df, filename=file.filename)

        logger.info(f"Upload bem-sucedido. arquivo={file.filename} linhas_processadas={len(df)}")

        return {
            "status": "sucesso",
            "linhas_processadas": int(len(df)),
            "arquivo_original": file.filename,
        }

    except DataValidationError as e:
        logger.error(f"Erro de validação no upload. arquivo={file.filename} erro={str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado no upload. arquivo={file.filename} erro={str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o arquivo.")

