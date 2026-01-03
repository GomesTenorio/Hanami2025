from __future__ import annotations
import pandas as pd

"""
Retorna lista de produtos com:
    - nome_produto
    - quantidade_vendida (soma de quantidade)
    - total_arrecadado (soma de valor_final)

    sort_by: "quantidade" | "total_arrecadado" | "nome"
    order: "asc" | "desc"
"""
def product_analysis(df: pd.DataFrame, sort_by: str = "total_arrecadado", order: str = "desc") -> list[dict]:
   
    if df is None or df.empty:
        return []

    # Garantias mínimas
    required = ["nome_produto", "quantidade", "valor_final"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Arquivo inválido. Coluna ausente para análise de produtos: {col}")

    grouped = (
        df.groupby("nome_produto", dropna=False)
        .agg(
            quantidade_vendida=("quantidade", "sum"),
            total_arrecadado=("valor_final", "sum"),
        )
        .reset_index()
    )

    # Normaliza tipos
    grouped["quantidade_vendida"] = pd.to_numeric(grouped["quantidade_vendida"], errors="coerce").fillna(0).astype(int)
    grouped["total_arrecadado"] = pd.to_numeric(grouped["total_arrecadado"], errors="coerce").fillna(0).astype(float)

    # Ordenação
    sort_by = (sort_by or "").strip().lower()
    order = (order or "desc").strip().lower()

    sort_map = {
        "quantidade": "quantidade_vendida",
        "total_arrecadado": "total_arrecadado",
        "nome": "nome_produto",
    }
    sort_col = sort_map.get(sort_by, "total_arrecadado")
    ascending = True if order == "asc" else False

    grouped = grouped.sort_values(by=sort_col, ascending=ascending)

    # Retorno em lista de dicts
    return [
        {
            "nome_produto": str(row["nome_produto"]),
            "quantidade_vendida": int(row["quantidade_vendida"]),
            "total_arrecadado": float(row["total_arrecadado"]),
        }
        for _, row in grouped.iterrows()
    ]
