#!/usr/bin/env python3
"""
run.py  –  Controla Weaviate + API FastAPI (v4 client)

Requisitos:
    pip install "weaviate-client>=4,<5" psutil
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import threading
import time
from contextlib import closing
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import psutil
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

# ───────────── Config ───────────── #
WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
DOCKER_COMPOSE_FILE: str = os.getenv("COMPOSE_FILE", "docker-compose.yml")
API_CMD: list[str] = [sys.executable, "scripts/start_api.py"]
API_PORT: int = int(os.getenv("API_PORT", 8000))
CHECK_INTERVAL = 2        # seg entre reintentos
READY_TIMEOUT = 60        # seg máx esperando Weaviate
GRPC_DEFAULT_PORT = 50051
# ────────────────────────────────── #


def build_connection_params(url: str) -> ConnectionParams:
    """Crea ConnectionParams desde una URL http[s]://host:port"""
    parsed = urlparse(url)
    grpc_secure = parsed.scheme == "https"
    return ConnectionParams.from_url(
        url=url,
        grpc_port=GRPC_DEFAULT_PORT,
        grpc_secure=grpc_secure,
    )


# ---------- Docker helpers ---------- #
def is_weaviate_running() -> bool:
    result = subprocess.run(
        ["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "ps", "-q", "weaviate"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


# ---------- Esperar a que Weaviate responda ---------- #
def wait_for_weaviate(url: str, timeout: int) -> None:
    conn_params = build_connection_params(url)
    client = WeaviateClient(connection_params=conn_params)

    start = time.time()
    while True:
        try:
            client.connect()             # ← necesario en v4
            if client.is_ready():
                client.close()
                return
        except Exception:
            pass

        if time.time() - start > timeout:
            client.close()
            raise TimeoutError("Weaviate no respondió a tiempo")

        time.sleep(CHECK_INTERVAL)


# ---------- Puertos locales ---------- #
def is_port_occupied(port: int) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def get_process_on_port(port: int) -> Optional[psutil.Process]:
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.AccessDenied, AttributeError):
            continue
    return None


# ---------- Main ---------- #
def main() -> None:
    os.chdir(Path(__file__).resolve().parent)

    started_weaviate = False
    api_process: Optional[subprocess.Popen] = None

    # 1) Weaviate
    if is_weaviate_running():
        print("Weaviate ya está en ejecución.")
    else:
        print("Iniciando contenedor Weaviate...")
        subprocess.run(
            ["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d", "weaviate"],
            check=True,
        )
        started_weaviate = True

    print("Esperando a que Weaviate esté listo...")
    wait_for_weaviate(WEAVIATE_URL, READY_TIMEOUT)
    print(f"✅ Weaviate responde en {WEAVIATE_URL}")

    # 2) API FastAPI
    if is_port_occupied(API_PORT):
        proc = get_process_on_port(API_PORT)
        msg = (
            f"⚠️  El puerto {API_PORT} ya está en uso "
            f"por PID {proc.pid} ({proc.name()})" if proc else
            f"⚠️  El puerto {API_PORT} está ocupado."
        )
        print(msg + " No se lanza la API.")
    else:
        print("Lanzando API:", " ".join(API_CMD))
        api_process = subprocess.Popen(API_CMD)

    # 3) Ctrl-C graceful shutdown
    stop_event = threading.Event()

    def handle_sigint(_signum, _frame):
        stop_event.set()

    signal.signal(signal.SIGINT, handle_sigint)

    print("Presiona Ctrl+C para salir.")
    stop_event.wait()

    # 4) Shutdown
    print("\nInterrupción recibida. Finalizando...")

    if api_process and api_process.poll() is None:
        api_process.terminate()
        try:
            api_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            api_process.kill()

    if started_weaviate:
        print("Deteniendo contenedor Weaviate...")
        subprocess.run(
            ["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "stop", "weaviate"],
            check=False,
        )

    print("Finalizado.")


if __name__ == "__main__":
    main()
