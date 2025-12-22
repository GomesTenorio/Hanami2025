from fastapi import FastAPI

app = FastAPI(
    title="Hanami Analytics API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.get("/health")
def health():
    return {"status": "ok"}

