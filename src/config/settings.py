# src/config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ruta base del proyecto, se usa para construir rutas relativas
# Esta ruta es la raíz del proyecto y se usa para definir otras rutas relativas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URL del servidor Weaviate, que se usa para almacenar y recuperar documentos
# Este URL debe apuntar a tu instancia de Weaviate, ya sea local o en la nube
# Se usa para la indexación y búsqueda de documentos legales
WEAVIATE_URL = os.getenv("WEAVIATE_URL")

# Verifica si se debe usar un LLM local o uno remoto
# Si USE_LOCAL_LLM es "true", se usará un modelo local, de lo contrario, se usará un modelo remoto
# Esta variable se usa para decidir si se conecta a un modelo local o a la API de OpenAI
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"

# Ruta al directorio de OneDrive, donde se almacenarán los documentos legales
# Este directorio se usa para sincronizar documentos desde OneDrive a la aplicación
ONEDRIVE_PATH = Path(os.getenv("ONEDRIVE_PATH", BASE_DIR / "onedrive"))

# Ruta a los documentos de entrada, donde se almacenarán los archivos originales para ingesta
# Estos documentos se procesarán para crear los chunks y el índice
DATA_RAW_PATH = Path(os.getenv("DATA_RAW_PATH", BASE_DIR / "data" / "raw"))

# Ruta a los chunks de datos, donde se almacenarán los fragmentos procesados de los documentos
# Estos chunks se usan para la búsqueda y recuperación de información relevante
DATA_CHUNKS_PATH = Path(os.getenv("DATA_CHUNKS_PATH", BASE_DIR / "data" / "chunks"))

# Ruta al índice de datos, donde se almacenarán los metadatos de los documentos
# Este índice se usa para la búsqueda y recuperación de documentos relevantes
DATA_INDEX_PATH = Path(os.getenv("DATA_INDEX_PATH", BASE_DIR / "data" / "index"))

# Verifica si el modo de simulación está activado
# Si USE_MOCK_MODE es "true", se simularán las respuestas sin usar el LLM real
# Si es "false", se usará el LLM real para generar respuestas
USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"

# Si DEBUG_PRINT_CONTEXT es "true", se imprimirá en consola el contexto recuperado
# antes de enviarlo al LLM. Útil para depuración.
DEBUG_PRINT_CONTEXT = os.getenv("DEBUG_PRINT_CONTEXT", "false").lower() == "true"

# Ruta a los documentos para ingesta
DOCS_INPUT_PATH = os.getenv("DOCS_INPUT_PATH", "data/raw")

# Ruta a los documentos procesados para chunks
# Esta ruta se usa para almacenar los fragmentos de documentos que se generarán a partir de los documentos de entrada
# Estos chunks se usarán para la búsqueda y recuperación de información relevante
DOCS_OUTPUT_PATH = os.getenv("DOCS_OUTPUT_PATH", "data/chunks")