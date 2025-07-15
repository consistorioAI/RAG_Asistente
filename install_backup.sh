#!/usr/bin/env bash
# Restaura un backup de Weaviate desde /data/weaviate_data/incoming/<archivo>.tar.gz
# Uso: ./install_backup.sh <archivo.tar.gz>

set -euo pipefail

CONTAINER="rag_asistente-weaviate-1"
DATA_ROOT="/data/weaviate_data"
INCOMING="$DATA_ROOT/incoming"
ARCHIVE="$DATA_ROOT/archivados"

FILE="${1:?Falta archivo .tar.gz}"
SRC="$INCOMING/$FILE"

[[ -f $SRC ]] || { echo "❌ No existe $SRC"; exit 1; }

echo "Parando contenedor $CONTAINER…"
sudo docker stop "$CONTAINER" >/dev/null

echo "🧹 Limpiando datos antiguos (se conservan incoming/ y archivados/)..."
find "$DATA_ROOT" -mindepth 1 -maxdepth 1 \
     ! -name incoming ! -name archivados \
     -exec rm -rf {} +

echo "Extrayendo backup en $DATA_ROOT..."
tar -xzf "$SRC" -C "$DATA_ROOT"

# Verificación mínima
[[ -f $DATA_ROOT/schema.db && -d $DATA_ROOT/legaldocs ]] \
  || { echo "❌ ERROR: schema.db o legaldocs faltan; restauración abortada."; exit 1; }

echo "Arrancando contenedor $CONTAINER..."
sudo docker start "$CONTAINER" >/dev/null

echo "📂 Archivando backup usado (moviendo a $ARCHIVE/)"
mkdir -p "$ARCHIVE"
mv "$SRC" "$ARCHIVE/"

echo "✅ Restauración completada. Comprueba las clases con:"
echo "   python scripts/show_classes.py"
