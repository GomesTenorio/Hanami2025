from __future__ import annotations
import pandas as pd


"""
    Calcula:
    - total_vendas: soma(valor_final)
    - numero_transacoes: quantidade de linhas
    - media_por_transacao: total_vendas / numero_transacoes
"""

def calculate_sales_metrics(df: pd.DataFrame) -> dict:

    if df is None or df.empty:
        return {"total_vendas": 0.0, "numero_transacoes": 0, "media_por_transacao": 0.0}

    total_vendas = float(df["valor_final"].fillna(0).sum())
    numero_transacoes = int(len(df))
    media_por_transacao = float(total_vendas / numero_transacoes) if numero_transacoes > 0 else 0.0

    return {
        "total_vendas": total_vendas,
        "numero_transacoes": numero_transacoes,
        "media_por_transacao": media_por_transacao,
    }

"""
Métricas financeiras consistentes com o dataset:

- receita_liquida: soma(valor_final) (já após descontos)
- lucro_bruto: soma(valor_final * margem_lucro/100)

Observação: margem_lucro é percentual (15-60).
"""

def calculate_financial_metrics(df: pd.DataFrame) -> dict:

    if df is None or df.empty:
        return {"receita_liquida": 0.0, "lucro_bruto": 0.0}

    receita_liquida = float(df["valor_final"].fillna(0).sum())

    # margem_lucro vem como percentual. Converte para decimal.
    margem = pd.to_numeric(df["margem_lucro"], errors="coerce").fillna(0) / 100.0
    lucro_bruto = float((df["valor_final"].fillna(0) * margem).sum())

    return {
        "receita_liquida": receita_liquida,
        "lucro_bruto": lucro_bruto,
    }
