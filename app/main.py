from fastapi import FastAPI
from app.api.routes.upload import router as upload_router


app = FastAPI(
    title="Hanami Analytics API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(upload_router)

@app.get("/health")
def health():
    return {"status": "ok"}

