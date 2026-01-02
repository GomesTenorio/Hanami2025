from __future__ import annotations

import os
import sys
from pathlib import Path
from loguru import logger

#Configurar logs no console e em arquivo.

def setup_logging(log_level: str = "INFO") -> None:

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Remove handlers padrão do loguru
    logger.remove()

    # Console
    logger.add(
        sys.stdout,
        level=log_level.upper(),
        backtrace=False,
        diagnose=False,
        enqueue=True,
    )

    # Arquivo
    logger.add(
        logs_dir / "app.log",
        level=log_level.upper(),
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=False,
        diagnose=False,
        enqueue=True,
    )