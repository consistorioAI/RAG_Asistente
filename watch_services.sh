#!/bin/bash

# watch_services.sh - Ensure Weaviate and the FastAPI service are running
#
# When executed periodically (e.g. via cron or a systemd timer) this script
# checks that the Weaviate container and the API are alive. Adjust the sleep
# duration at the end if you use it in a loop.

PROJECT_DIR="/home/consistorioai/RAG_Asistente"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"
LOG_FILE="$PROJECT_DIR/rag_api.log"

cd "$PROJECT_DIR" || exit 1

# 1) Verify Weaviate container
WEAVIATE_ID=$(docker compose -f docker-compose.yml ps -q weaviate)
if [ -z "$WEAVIATE_ID" ]; then
    echo "$(date) - Weaviate no está activo. Iniciando..."
    docker compose -f docker-compose.yml up -d weaviate
else
    echo "$(date) - Weaviate en ejecución."
fi

# 2) Verify API process
if pgrep -f "python.*run.py" > /dev/null; then
    echo "$(date) - API en ejecución."
else
    echo "$(date) - API caída. Reiniciando..."
    # Liberamos el puerto 8000 si estuviera ocupado
    if command -v fuser >/dev/null 2>&1; then
        fuser -k 8000/tcp || true
    elif command -v lsof >/dev/null 2>&1; then
        lsof -ti:8000 | xargs -r kill -9
    fi
    # Lanzamos la API igual que en start_server.sh
    source "$VENV_PATH"
    nohup python run.py >> "$LOG_FILE" 2>&1 &
    echo "$(date) - API reiniciada con PID $!"
fi

