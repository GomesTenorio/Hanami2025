from __future__ import annotations

from typing import Iterable, Optional
import pandas as pd


def normalize_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower() #converte para string, remove espaços extras e coloca em minúsculas


def require_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Arquivo inválido. Colunas ausentes: {missing}")


def coerce_numeric(df: pd.DataFrame, col: str) -> pd.DataFrame: #converte para número, valores inválidos viram NaN
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def coerce_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame: #converte para datetime, valores inválidos viram NaT
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def clean_nulls(
    df: pd.DataFrame,
    critical_cols: Iterable[str],
    fill_defaults: Optional[dict[str, object]] = None,
    drop_if_null: bool = True,
) -> pd.DataFrame:

    if fill_defaults:
        for k, v in fill_defaults.items():
            if k in df.columns:
                df[k] = df[k].fillna(v)

    if drop_if_null:
        df = df.dropna(subset=list(critical_cols))

    return df

    """
    Regra simples e previsível da  estrutura:
    - Se drop_if_null=True remove linhas onde coluna crítica é nula
    - Se fill_defaults é fornecido, preenche nulos com default antes de dropar (se quiser)
    """
