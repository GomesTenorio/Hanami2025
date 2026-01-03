# Hanami 2025

# CSV/XLSX Analytics API

API para processamento de arquivos CSV/XLSX e geração de relatórios analíticos.

**Swagger UI:** http://127.0.0.1:8000/docs

**OpenAPI JSON:** http://127.0.0.1:8000/openapi.json

## Sprint 1

1. Setup do Ambiente e Projeto
2. Módulo de Leitura e Validação de Dados
3. Endpoint POST /upload
4. Configuração de Logging
5. Módulo de Cálculos (Finanças e Vendas)
6. Endpoints de Vendas e Produtos
7. Endpoint de Métricas Financeiras

**Observações:**

- Projeto focado em API, sem front-end (Swagger é a interface de uso)
- O dataset é armazenado em memória
- O servidor limpa os dados carregados quando é reiniciado

## Requisitos

- Python 3.10+
- pip ou poetry

## Instalação

```bash
git clone <repo>
cd Hanami2025
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt #Instalar dependências
```

## Configurar variáveis de ambiente

```bash
copy .env.example .env # Windows
cp .env.example .env # Linux/Mac
```

## Executar a API

```bash
bash ou PowerShell:
python -m uvicorn app.main:app --reload

Saída: Uvicorn running on http://127.0.0.1:8000
```

## Fluxo básico da API

1. POST /upload: Upload do arquivo
2. Relatórios disponíveis:
   - GET /reports/sales-summary
   - GET /reports/financial-metrics
   - GET /reports/product-analysis
3. Verificar status do dataset
   - GET /dataset/status

**Logs são exibidos no console e gravados em logs/app.log** - INFO: uploads bem-sucedidos - ERROR: erros de validação/processamento

## Regras de Cálculo usadas

```bash
- total_vendas = soma de valor_final
- media_por_transacao = total_vendas / número de transações
- receita_liquida = soma de valor_final
- lucro_bruto = soma de (valor_final * margem_lucro / 100)
- custo_total = receita_liquida - lucro_bruto

Obs: Custos são estimados a partir da margem de lucro informada no dataset.
```

---

Created by me ( ͡° ͜ʖ ͡°)

---
