from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.core.errors import DataValidationError
from app.core.storage import InMemoryDataset, CURRENT_DATASET
from app.services.parser import read_file_to_dataframe


router = APIRouter(tags=["upload"])

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(None)):
    if file is None:
        raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado.") # 400 nenhum arquivo enviado

    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422, # 422 arquivo inválido e o tipo
            detail=f"Formato inválido. Envie um arquivo CSV ou XLSX. Recebido: {suffix or 'sem extensão'}",
        )

    # garante que a pasta existe
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # salva com nome único
    safe_name = f"{uuid4().hex}{suffix}"
    saved_path = UPLOAD_DIR / safe_name

    try:
        content = await file.read()
        saved_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao salvar o arquivo. Detalhe: {str(e)}")

    # parse + valida + limpa
    try:
        df = read_file_to_dataframe(saved_path)
    except DataValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) # 422: inválido (colunas faltando, leitura falhou, etc.)

    # guarda em memória para próximos endpoints
    import app.core.storage as storage
    storage.CURRENT_DATASET = InMemoryDataset(df=df, filename=filename, uploaded_at=datetime.utcnow())

    return JSONResponse(
        status_code=200,
        content={
            "status": "sucesso",
            "linhas_processadas": int(len(df)),
            "arquivo_original": filename,
        },
    )
