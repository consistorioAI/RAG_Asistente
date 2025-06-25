# src/config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ruta base del proyecto, se usa para construir rutas relativas
# Esta ruta es la raíz del proyecto y se usa para definir otras rutas relativas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Nombre del modelo de OpenAI que se usará para la generación de texto
# Este modelo se usará para generar respuestas a preguntas legales
# Puedes cambiarlo según el modelo que desees usar, por ejemplo, "gpt-3.5-turbo" o "gpt-4"
# El valor por defecto es "gpt-4o", que es un modelo optimizado de OpenAI
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

# URL del servidor Weaviate, que se usa para almacenar y recuperar documentos
# Este URL debe apuntar a tu instancia de Weaviate, ya sea local o en la nube
# Se usa para la indexación y búsqueda de documentos legales
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# Verifica si se debe usar un LLM local o uno remoto
# Si USE_LOCAL_LLM es "true", se usará un modelo local, de lo contrario, se usará un modelo remoto
# Esta variable se usa para decidir si se conecta a un modelo local o a la API de OpenAI
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
LLM_MODEL_PATH = Path(os.getenv("LLM_MODEL_PATH", BASE_DIR / "models" / "mistral-7b-instruct-v0.1.Q4_K_M.gguf"))
LLM_MODEL_URL = os.getenv("LLM_MODEL_URL", "http://localhost:8001")

# Ruta al directorio de OneDrive, donde se almacenarán los documentos legales
# Este directorio se usa para sincronizar documentos desde OneDrive a la aplicación
ONEDRIVE_PATH = Path(os.getenv("ONEDRIVE_PATH", BASE_DIR / "onedrive"))

# Credenciales para conectar con OneDrive
ONEDRIVE_CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")
ONEDRIVE_CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET")
ONEDRIVE_TENANT_ID = os.getenv("ONEDRIVE_TENANT_ID")
ONEDRIVE_DRIVE_ID = os.getenv("ONEDRIVE_DRIVE_ID")
ONEDRIVE_FOLDER = os.getenv("ONEDRIVE_FOLDER", "")  # carpeta raíz por defecto

# Habilita la descarga automática de archivos desde OneDrive
USE_ONEDRIVE = os.getenv("USE_ONEDRIVE", "false").lower() == "false"

# Futuro endpoint público (p.ej. URL de despliegue de la API)
ENTRYPOINT_URL = os.getenv("ENTRYPOINT_URL")

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

# Clave para autenticación de la API FastAPI
API_KEY = os.getenv("API_KEY")

# Ruta a los documentos para ingesta
DOCS_INPUT_PATH = os.getenv("DOCS_INPUT_PATH", "data/raw")

# Ruta a los documentos procesados para chunks
# Esta ruta se usa para almacenar los fragmentos de documentos que se generarán a partir de los documentos de entrada
# Estos chunks se usarán para la búsqueda y recuperación de información relevante
DOCS_OUTPUT_PATH = os.getenv("DOCS_OUTPUT_PATH", "data/chunks")

# Tamaño y solapamiento de los chunks para la indexación
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Límite máximo de tokens a enviar como contexto al modelo
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "3000"))

# Límite máximo de tokens generados por el modelo para cada respuesta
MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "800"))

# Número de documentos a recuperar por el retriever si no se especifica otro valor
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "5"))

