#!/usr/bin/env python3
"""
run.py

- Inicia el contenedor Weaviate si no está ya en ejecución.
- Espera hasta que Weaviate esté accesible.
- Lanza la API FastAPI si el puerto 8000 está libre.
- Captura Ctrl+C para cerrar procesos que inició este script.

Requisitos:
    pip install weaviate-client psutil
"""

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

import psutil
from weaviate import WeaviateClient

# Configuración
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
DOCKER_COMPOSE_FILE = os.getenv("COMPOSE_FILE", "docker-compose.yml")
API_CMD = [sys.executable, "scripts/start_api.py"]
API_PORT = int(os.getenv("API_PORT", 8000))
CHECK_INTERVAL = 2
READY_TIMEOUT = 60


def is_weaviate_running() -> bool:
    """Devuelve True si el contenedor weaviate está activo."""
    result = subprocess.run(
        ["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "ps", "-q", "weaviate"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def wait_for_weaviate(url: str, timeout: int) -> None:
    """Espera hasta que Weaviate responda o se agote el tiempo."""
    client = WeaviateClient(url)
    start_time = time.time()
    while True:
        try:
            if client.is_ready():
                return
        except Exception:
            pass
        if time.time() - start_time > timeout:
            raise TimeoutError("Weaviate no respondió a tiempo")
        time.sleep(CHECK_INTERVAL)


def is_port_occupied(port: int) -> bool:
    """Verifica si hay algo escuchando en localhost:port."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def get_process_on_port(port: int) -> Optional[psutil.Process]:
    """Devuelve el proceso que usa el puerto indicado, si existe."""
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            connections = proc.net_connections(kind="inet")
        except (psutil.AccessDenied, AttributeError):
            continue
        for conn in connections:
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                return proc
    return None


def main() -> None:
    os.chdir(Path(__file__).resolve().parent)

    started_weaviate = False
    api_process: Optional[subprocess.Popen] = None

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
    print(f"Weaviate responde en {WEAVIATE_URL}")

    if is_port_occupied(API_PORT):
        proc = get_process_on_port(API_PORT)
        if proc:
            print(f"El puerto {API_PORT} ya está en uso por PID {proc.pid} ({proc.name()}). No se lanza la API.")
        else:
            print(f"El puerto {API_PORT} está ocupado. No se lanza la API.")
    else:
        print("Lanzando API:", " ".join(API_CMD))
        api_process = subprocess.Popen(API_CMD)

    stop_event = threading.Event()

    def handle_sigint(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, handle_sigint)

    print("Presiona Ctrl+C para salir.")
    stop_event.wait()

    print("Interrupción recibida. Finalizando...")

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
