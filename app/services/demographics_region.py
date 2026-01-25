from __future__ import annotations

import pandas as pd


def _require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Arquivo inválido. Colunas ausentes: {missing}")


def regional_metrics(df: pd.DataFrame) -> list[dict]:
    """
    Agrupa por regiao e calcula métricas por região.

    Retorna lista de dicts:
    [
      {
        "regiao": "sudeste",
        "total_vendas": 123.45,
        "numero_transacoes": 1000,
        "media_por_transacao": 0.12
      }, ...
    ]
    """
    if df is None or df.empty:
        return []

    _require_columns(df, ["regiao", "valor_final"])

    grouped = (
        df.groupby("regiao", dropna=False)
        .agg(
            total_vendas=("valor_final", "sum"),
            numero_transacoes=("valor_final", "size"),
        )
        .reset_index()
    )

    grouped["total_vendas"] = pd.to_numeric(grouped["total_vendas"], errors="coerce").fillna(0).astype(float)
    grouped["numero_transacoes"] = pd.to_numeric(grouped["numero_transacoes"], errors="coerce").fillna(0).astype(int)
    grouped["media_por_transacao"] = grouped.apply(
        lambda r: float(r["total_vendas"] / r["numero_transacoes"]) if r["numero_transacoes"] > 0 else 0.0,
        axis=1,
    )

    # Ordena por total_vendas desc (mais relevante primeiro)
    grouped = grouped.sort_values(by="total_vendas", ascending=False)

    return [
        {
            "regiao": str(row["regiao"]),
            "total_vendas": float(row["total_vendas"]),
            "numero_transacoes": int(row["numero_transacoes"]),
            "media_por_transacao": float(row["media_por_transacao"]),
        }
        for _, row in grouped.iterrows()
    ]


def customer_distribution(df: pd.DataFrame) -> dict:
    """
    Calcula distribuição (contagem e percentual) de clientes por:
    - genero_cliente
    - faixa_etaria (a partir de idade_cliente)
    - cidade_cliente

    Retorna dict com 3 listas:
    {
      "genero": [{"genero_cliente":"f","count":..., "percent":...}, ...],
      "faixa_etaria": [{"faixa":"18-24","count":...,"percent":...}, ...],
      "cidade": [{"cidade_cliente":"São Paulo","count":...,"percent":...}, ...]
    }

    Observação: usa o total de linhas como base de percentuais.
    """
    if df is None or df.empty:
        return {"genero": [], "faixa_etaria": [], "cidade": []}

    _require_columns(df, ["genero_cliente", "idade_cliente", "cidade_cliente"])

    total = int(len(df)) if len(df) > 0 else 1

    # 1) Gênero
    genero_series = df["genero_cliente"].astype(str).str.strip().str.lower()
    genero_counts = genero_series.value_counts(dropna=False)

    genero = [
        {
            "genero_cliente": str(idx),
            "count": int(cnt),
            "percent": float((cnt / total) * 100),
        }
        for idx, cnt in genero_counts.items()
    ]

    # 2) Faixa etária
    idade = pd.to_numeric(df["idade_cliente"], errors="coerce")

    # Bins padrão (você pode ajustar depois)
    bins = [0, 17, 24, 34, 44, 54, 64, 200]
    labels = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

    faixa = pd.cut(idade, bins=bins, labels=labels, include_lowest=True)
    faixa_counts = faixa.value_counts(dropna=False).reindex(labels, fill_value=0)

    faixa_etaria = [
        {
            "faixa": str(idx),
            "count": int(cnt),
            "percent": float((cnt / total) * 100),
        }
        for idx, cnt in faixa_counts.items()
    ]

    # 3) Cidade
    cidade_series = df["cidade_cliente"].astype(str).str.strip()
    cidade_counts = cidade_series.value_counts(dropna=False)

    cidade = [
        {
            "cidade_cliente": str(idx),
            "count": int(cnt),
            "percent": float((cnt / total) * 100),
        }
        for idx, cnt in cidade_counts.items()
    ]

    return {
        "genero": genero,
        "faixa_etaria": faixa_etaria,
        "cidade": cidade,
    }

def customer_profile_as_object(df: pd.DataFrame) -> dict:
    """
    Retorna distribuições como objetos para facilitar consumo:
    {
      "genero": {"m": {"count": 10, "percent": 50.0}, "f": {...}},
      "faixa_etaria": {"18-24": {"count":..., "percent":...}, ...},
      "cidade": {"maceio": {"count":..., "percent":...}, ...}
    }
    """
    dist = customer_distribution(df)

    def to_obj(items: list[dict], key_field: str) -> dict:
        out = {}
        for item in items:
            k = str(item.get(key_field))
            out[k] = {"count": int(item.get("count", 0)), "percent": float(item.get("percent", 0.0))}
        return out

    return {
        "genero": to_obj(dist["genero"], "genero_cliente"),
        "faixa_etaria": to_obj(dist["faixa_etaria"], "faixa"),
        "cidade": to_obj(dist["cidade"], "cidade_cliente"),
    }
