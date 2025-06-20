# scripts/start_api.py

import uvicorn
from pathlib import Path
import sys

# Añadir la raíz del proyecto al path para que se pueda importar `src.api.main`
sys.path.append(str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    # No usar reload en Windows, rompe multiprocessing + imports
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=False)
