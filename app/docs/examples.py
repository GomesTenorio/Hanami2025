SALES_SUMMARY_EXAMPLE = {
    "total_vendas": 12345678.9,
    "numero_transacoes": 10000,
    "media_por_transacao": 1234.56,
}

FINANCIAL_METRICS_EXAMPLE = {
    "receita_liquida": 12345678.9,
    "lucro_bruto": 3456789.12,
    "custo_total": 8888889.78,
}

PRODUCT_ANALYSIS_EXAMPLE = [
    {"nome_produto": "Cabo USB-C", "quantidade_vendida": 1131, "total_arrecadado": 4105439.98},
    {"nome_produto": "Webcam HD", "quantidade_vendida": 1144, "total_arrecadado": 3941456.24},
]

REGIONAL_PERFORMANCE_EXAMPLE = {
    "sudeste": {"total_vendas": 6000000.0, "numero_transacoes": 4500, "media_por_transacao": 1333.33},
    "nordeste": {"total_vendas": 3000000.0, "numero_transacoes": 2500, "media_por_transacao": 1200.0},
}

CUSTOMER_PROFILE_EXAMPLE = {
    "genero": {
        "m": {"count": 6000, "percent": 60.0},
        "f": {"count": 4000, "percent": 40.0},
    },
    "faixa_etaria": {
        "18-24": {"count": 1200, "percent": 12.0},
        "25-34": {"count": 2500, "percent": 25.0},
        "35-44": {"count": 1800, "percent": 18.0},
    },
    "cidade": {
        "maceio": {"count": 300, "percent": 3.0},
        "sao paulo": {"count": 1200, "percent": 12.0},
    },
}

DATASET_STATUS_EXAMPLE_LOADED = {
    "loaded": True,
    "arquivo_original": "vendas_ficticias_10000_linhas.csv",
    "uploaded_at": "2026-01-03T00:00:00Z",
    "linhas_processadas": 10000,
    "colunas": ["id_transacao", "data_venda", "valor_final"],
}

DOWNLOAD_ERROR_EXAMPLE = {"detail": "Formato inválido. Use format=json ou format=pdf."}
