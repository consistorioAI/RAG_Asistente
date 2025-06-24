# run.py

import yaml
import time
from pathlib import Path
from pyngrok import ngrok
import subprocess
import os

BASE_DIR = Path(__file__).resolve().parent
OPENAPI_PATH = BASE_DIR / "openapi.yaml"
LLM_MODEL_PATH = Path(os.getenv("LLM_MODEL_PATH", BASE_DIR / "models" / "mistral-7b-instruct-v0.1.Q4_K_M.gguf"))
PORT_API = 8000
PORT_LLM = 8001

def start_ngrok_and_update_yaml():
    print("[run] Iniciando ngrok y actualizando openapi.yaml...")
    public_url = ngrok.connect(PORT_API, bind_tls=True).public_url
    print(f"[run] URL pública ngrok: {public_url}")

    with OPENAPI_PATH.open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    spec["servers"] = [{"url": public_url}]

    with OPENAPI_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(spec, f, allow_unicode=True)

    return public_url

def open_powershell(command, title):
    full_command = [
        "powershell.exe",
        "-NoExit",
        "-Command",
        f"$Host.UI.RawUI.WindowTitle = '{title}'; {command}"
    ]
    subprocess.Popen(full_command, creationflags=subprocess.CREATE_NEW_CONSOLE)


if __name__ == "__main__":
    print("[run] === ENTORNO DE DESARROLLO RAG ===")

    # 1. Iniciar ngrok y actualizar el YAML
    public_url = start_ngrok_and_update_yaml()
    print(f"[run] Túnel activo: {public_url}")

    # 2. Abrir terminal para el LLM
    print("[run] Abriendo terminal para el modelo LLM...")
    open_powershell(
        f'python -m llama_cpp.server --model "{LLM_MODEL_PATH}" --n_ctx 4096 --n_threads 8 --n_gpu_layers 32 --port {PORT_LLM}',
        "LLM Server (llama-cpp)"
    )

    time.sleep(5)  # esperar a que cargue el modelo

    # 3. Abrir terminal para la API FastAPI
    print("[run] Abriendo terminal para API FastAPI...")
    open_powershell(
        f'python scripts/start_api.py',
        "RAG API"
    )

    # 4. Abrir terminal para ngrok visualmente (opcional, ya está en uso por pyngrok)
    print("[run] Abriendo terminal para ngrok (opcional)...")
    open_powershell(
        f'ngrok http {PORT_API}',
        "ngrok tunnel"
    )

    print("\n[run] ✅ Entorno de desarrollo iniciado.")
    print(f"[run] Accede a tu API en: {public_url}/docs")
    print("[run] Usa Ctrl+C en cada terminal para cerrar manualmente.")
