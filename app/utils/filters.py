from __future__ import annotations

from datetime import date, datetime
import pandas as pd


def parse_yyyy_mm_dd(value: str) -> date:
    """
    Converte 'YYYY-MM-DD' em date. Levanta ValueError com mensagem clara.
    """
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Data inválida: '{value}'. Use o formato YYYY-MM-DD.")


def filter_by_date_range(df: pd.DataFrame, date_col: str, start: date | None, end: date | None) -> pd.DataFrame:
    """
    Filtra por intervalo de datas (inclusivo). Assume df[date_col] já convertido para datetime.
    """
    if start is None and end is None:
        return df

    if date_col not in df.columns:
        return df

    s = pd.Timestamp(start) if start else None
    e = pd.Timestamp(end) if end else None

    mask = pd.Series([True] * len(df), index=df.index)
    if s is not None:
        mask = mask & (df[date_col] >= s)
    if e is not None:
        mask = mask & (df[date_col] <= e)

    return df.loc[mask]


def filter_by_estado(df: pd.DataFrame, estado: str | None) -> pd.DataFrame:
    """
    Filtra por estado. Normaliza para uppercase e strip.
    """
    if not estado:
        return df

    if "estado_cliente" not in df.columns:
        return df

    uf = estado.strip().upper()
    return df.loc[df["estado_cliente"].astype(str).str.strip().str.upper() == uf]
