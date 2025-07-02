#!/bin/bash

echo "🔍 Buscando procesos activos de run.py..."
PIDS=$(pgrep -f "python.*run.py")

if [ -z "$PIDS" ]; then
  echo "✅ No hay procesos activos de run.py."
  exit 0
fi

echo "⛔ Deteniendo procesos: $PIDS"
kill $PIDS

# Esperamos a que mueran (1s por seguridad)
sleep 1

# Verificamos
REMAINING=$(pgrep -f "python.*run.py")
if [ -z "$REMAINING" ]; then
  echo "✅ Todos los procesos fueron detenidos correctamente."
else
  echo "⚠️ Algunos procesos siguen vivos: $REMAINING"
  echo "Puedes forzarlos con: kill -9 $REMAINING"
fi
