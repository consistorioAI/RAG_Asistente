#!/bin/bash

# Ruta absoluta del proyecto (ajústalo si es necesario)
PROJECT_DIR="/home/consistorioai/RAG_Asistente"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

# Directorio donde se almacenarán los logs rotados por fecha
LOG_DIR="/home/consistorioai/logs"
mkdir -p "$LOG_DIR"
# Nombre del log actual basado en la fecha
LOG_FILE="$LOG_DIR/rag_api_$(date +%F).log"

# Entra al directorio del proyecto
cd "$PROJECT_DIR" || exit 1

# Activa el entorno virtual
source "$VENV_PATH"

# Lanza el script de arranque de la API en background, ignorando la desconexión
nohup python run.py > "$LOG_FILE" 2>&1 &

# Opcional: muestra el PID y dónde ver logs
echo "✅ API iniciada con PID $! (log en $LOG_FILE)"
