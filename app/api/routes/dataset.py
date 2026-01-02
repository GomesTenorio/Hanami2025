from fastapi import APIRouter
import app.core.storage as storage

router = APIRouter(tags=["dataset"])


@router.get("/dataset/status")
def dataset_status():
    if storage.CURRENT_DATASET is None:
        return {
            "loaded": False,
            "message": "Nenhum dataset carregado. Faça upload em /upload.",
        }

    ds = storage.CURRENT_DATASET
    return {
        "loaded": True,
        "arquivo_original": ds.filename,
        "uploaded_at": ds.uploaded_at.isoformat(),
        "linhas_processadas": int(len(ds.df)),
        "colunas": list(ds.df.columns),
    }
