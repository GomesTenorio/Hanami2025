from __future__ import annotations

from pathlib import Path
import pandas as pd

from fastapi import UploadFile
import tempfile


from app.core.errors import DataValidationError
from app.utils.validators import (
    require_columns,
    clean_nulls,
    coerce_numeric,
    coerce_datetime,
    normalize_text,
)

EXPECTED_COLUMNS = [
    "valor_final",
    "idade_cliente",
    "data_venda",
    "canal_venda",
]

CRITICAL_COLUMNS = [
    "valor_final",
]

TEXT_COLUMNS = [
    "canal_venda",
    "forma_pagamento",
    "regiao",
    "status_entrega",
    "genero_cliente",
    "cidade_cliente",
    "estado_cliente",
    "categoria",
    "marca",
    "nome_produto",
]

NUMERIC_COLUMNS = [
   "valor_final",
   "idade_cliente",
   "subtotal",
   "desconto_percent",
   "preco_unitario",
   "quantidade",
   "margem_lucro",
   "renda_estimada",
   "tempo_entrega_dias", 
]

DATE_COLUMNS = [
    "data_venda",
]


def read_file_to_dataframe(file_path: str | Path) -> pd.DataFrame:
    """
    Lê CSV ou XLSX e retorna um DataFrame já validado e padronizado.
    Levanta DataValidationError com mensagem clara em caso de problema.
    """
    path = Path(file_path)

    if not path.exists():
        raise DataValidationError(f"Arquivo não encontrado: {path}")

    suffix = path.suffix.lower()

    try:
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            raise DataValidationError("Formato inválido. Envie um arquivo .csv ou .xlsx")
    except Exception as e:
        raise DataValidationError(f"Falha ao ler o arquivo. Detalhe: {str(e)}")

    # Padroniza nomes de colunas (evita erro por espaços ou case)
    df.columns = [str(c).strip() for c in df.columns]

    # Validação de colunas esperadas
    try:
        require_columns(df, EXPECTED_COLUMNS)
    except ValueError as e:
        raise DataValidationError(str(e))

    # Limpeza de nulos em colunas críticas
    df = clean_nulls(df, critical_cols=CRITICAL_COLUMNS, drop_if_null=True)

    # Conversão de tipos: numéricos
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df = coerce_numeric(df, col)

    # Conversão de tipos: datas
    for col in DATE_COLUMNS:
        if col in df.columns:
            df = coerce_datetime(df, col)

    # Depois das conversões, removemos linhas que ficaram inválidas nas críticas
    df = df.dropna(subset=CRITICAL_COLUMNS)

    # Padronização de texto
    for col in TEXT_COLUMNS:
        if col in df.columns:
            df[col] = normalize_text(df[col])

    return df

async def parse_upload_to_dataframe(file: UploadFile) -> pd.DataFrame:
    """
    Recebe UploadFile (FastAPI), salva temporariamente e reutiliza read_file_to_dataframe
    para validar e padronizar.
    """
    suffix = Path(file.filename).suffix.lower()

    if suffix not in [".csv", ".xlsx", ".xls"]:
        raise DataValidationError("Formato inválido. Envie um arquivo .csv ou .xlsx")

    # Salva temporariamente para reutilizar a mesma rotina de validação
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        content = await file.read()
        tmp.write(content)

    try:
        df = read_file_to_dataframe(tmp_path)
        return df
    finally:
        # remove o arquivo temporário
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


