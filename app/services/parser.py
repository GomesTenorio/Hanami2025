from __future__ import annotations

from pathlib import Path
import pandas as pd

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
