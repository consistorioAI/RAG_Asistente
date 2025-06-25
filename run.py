#!/usr/bin/env python3
"""Utility script to launch Weaviate and the API service."""
import subprocess
import time
import sys
import signal

import weaviate

WEAVIATE_URL = "http://localhost:8080"
CHECK_INTERVAL = 2
TIMEOUT = 60


def wait_for_weaviate(url: str = WEAVIATE_URL, timeout: int = TIMEOUT) -> None:
    """Poll the Weaviate instance until it reports readiness."""
    client = weaviate.Client(url)
    start = time.time()
    while True:
        try:
            if client.is_ready():
                return
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError("Timed out waiting for Weaviate")
        time.sleep(CHECK_INTERVAL)


def main() -> None:
    # Start Weaviate container
    subprocess.run(["docker", "compose", "up", "-d", "weaviate"], check=True)

    print("Waiting for Weaviate to become ready...")
    wait_for_weaviate()
    print("Weaviate is ready.")

    api_process = subprocess.Popen([sys.executable, "scripts/start_api.py"])

    try:
        api_process.wait()
    except KeyboardInterrupt:
        print("Interrupted, shutting down...")
        api_process.terminate()
        try:
            api_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            api_process.kill()
    finally:
        subprocess.run(["docker", "compose", "down"], check=False)


if __name__ == "__main__":
    main()
