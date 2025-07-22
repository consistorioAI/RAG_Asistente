# scripts/start_api.py

from __future__ import annotations

import os
import sys
from pathlib import Path
import logging
from logging.config import dictConfig

# 1️⃣  AÑADIR LA RAÍZ **ANTES** DE CUALQUIER IMPORT DE `src`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import settings  # noqa: E402  ← ahora sí funciona

import uvicorn  # noqa: E402  (se importa después para mantener orden lógico)

# Configuración de logging para que cada entrada incluya fecha y hora
LOG_FORMAT = "%(asctime)s %(levelname)s:     %(message)s"
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {"format": LOG_FORMAT},
        "access": {"format": LOG_FORMAT},
    },
    "handlers": {
        "default": {"class": "logging.StreamHandler", "formatter": "default"},
        "access": {"class": "logging.StreamHandler", "formatter": "access"},
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)

if __name__ == "__main__":
    # No usar reload en Windows, rompe multiprocessing + imports
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "2"))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=workers,
        log_config=LOGGING_CONFIG,
    )
