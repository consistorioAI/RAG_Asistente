# scripts/start_api.py

import uvicorn
from pathlib import Path
import sys
from src.config import settings
import os

# Añadir la raíz del proyecto al path para que se pueda importar `src.api.main`
sys.path.append(str(Path(__file__).resolve().parent.parent))

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
    )
