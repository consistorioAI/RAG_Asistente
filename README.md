
**Fecha de corte: Última integración verificada con GPT personalizado y respuesta simulada vía API**

---

### **Introducción**

Este asistente implementa un sistema de generación aumentada por recuperación (RAG) orientado a consultas legales municipales. Los documentos se ingestan de forma local o desde OneDrive y se indexan en Weaviate. Un modelo de lenguaje local o de OpenAI genera las respuestas, accesibles mediante una API REST o a través de un plugin de ChatGPT.

Entre los casos de uso habituales se encuentran la resolución de consultas jurídicas y el soporte documental interno.


### **FASE 1: Preparación del entorno**

- Creación del entorno virtual con `venv`
    
- Instalación de dependencias base:
    
    - `langchain`, `langserve`, `openai`, `weaviate-client`, `python-dotenv`, `sentence-transformers`, `fastapi`, `uvicorn`, `pymupdf`, `python-docx`, `boxsdk`
        
- Configuración del archivo `.env` con claves necesarias
    
- Creación de estructura de carpetas del proyecto y archivo `run.py` de validación
    

---

### **FASE 2: Ingesta de documentos locales**

- Creación del módulo `ingestor.py` en `src/ingestion/`
    
- Extracción de texto desde documentos `.pdf`, `.docx` y `.txt`
    
- Generación de archivos `.txt` en `data/chunks/`
    
- Creación de metadatos asociados: nombre de archivo, ruta, fecha
    
- Script de ejecución: `scripts/ingest_local_docs.py`
- La lectura local ahora recorre `data/raw` y todas sus subcarpetas de forma
  recursiva

- Verificación de extracción correcta en entorno local
    

---

### **FASE 3: Chunking, generación de embeddings e indexación**

- División de los documentos en chunks usando `RecursiveCharacterTextSplitter`
    
- Uso de embeddings locales con modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Para acelerar la generación de embeddings se puede configurar `EMBEDDING_DEVICE=cuda` y ajustar `BATCH_SIZE` en `.env`

- Weaviate connection (probado con weaviate-client v4.x)
    
- Ajustes en el schema de Weaviate:
    
    - Definición de clase `LegalDocs`
        
    - Uso de `vectorizer: none`
        
    - Verificación de existencia de clase usando `client.schema.get()["classes"]`
        
- Indexación exitosa de los vectores en Weaviate vía `langchain_weaviate.WeaviateVectorStore`
    
- Script de ejecución: `scripts/index_chunks.py`
    
- Confirmación final: "Chunks indexados correctamente en Weaviate"
    

---

### **FASE 4: Visualización de embeddings**

- Creación del script `scripts/list_embeddings.py`
    
- Consulta GraphQL a Weaviate para recuperar texto y vectores
    
- Verificación de vectores:
    
    - Se muestra el texto original
        
    - Se muestra el vector asociado (parcialmente)
        
    - Se comprueba la dimensión de los vectores
        

---

### **FASE 5: Recuperación semántica**

- Creación del módulo `src/rag_logic/retriever_module.py` con `get_retriever(k)`
    
- Conexión del `retriever` con Weaviate + embeddings locales
    
- Script de prueba interactiva `scripts/query_retriever.py`
    
- Validación funcional: recuperación coherente y contextual de chunks ante consultas en lenguaje natural
    

---

### **FASE 6: Generación de respuestas con LLM local**

- Decisión de usar modelo local para evitar consumo de tokens de la API
    
- Instalación y configuración de `llama-cpp-python`
    
- Descarga y uso del modelo `mistral-7b-instruct-v0.1.Q4_K_M.gguf`
    
- Creación del wrapper `get_local_llm()` en `src/rag_logic/llm_local.py`
    
- Integración modular en `generator.py`, respetando `use_local` (controlado vía `.env`)
    
- Inclusión de `PromptTemplate` para forzar la respuesta en español
    
- Generación de respuestas naturales basada en chunks recuperados
    

---

### **FASE 7: Interfaz de pruebas limpia y continua**

- Actualización del script `scripts/query_generator.py`:
    
    - Ocultación de warnings y stderr
        
    - Entrada interactiva continua con bucle `while True`
        
    - Opción de cierre por `Ctrl+C` o `"salir"`
        
    - Salida clara: solo prompt, respuesta y fuentes relevantes
        
- Confirmación de funcionamiento completo:
    
    - Preguntas procesadas por LLM local
        
    - Respuestas generadas con base en documentos reales
        
    - Contexto mostrado y metadatos consultables
        

---

### **FASE 8: Exposición del sistema como API REST**

- Creación del endpoint `/query` usando FastAPI
    
- Estructura de entrada/salida validada con Pydantic (`QueryRequest`, `QueryResponse`)
    
- Pruebas exitosas con Swagger UI y Postman
    
- Adaptación para control desde `.env` (`USE_LOCAL_LLM`)
    
- Adaptación para retornar respuesta simulada (`USE_MOCK_MODE=true`) durante pruebas
- Nueva variable `DEBUG_PRINT_CONTEXT=true` permite mostrar en consola el contexto
  enviado al LLM para depuración
- Variables `MAX_CONTEXT_TOKENS` y `MAX_COMPLETION_TOKENS` permiten ajustar los
  límites de tokens de contexto y respuesta al usar la API de OpenAI
- Se añadió autenticación por cabecera `X-API-Key` y reutilización de clientes para mejorar el rendimiento
- Nueva variable `RETRIEVER_K` define cuántos documentos recupera el sistema por defecto
    

---

### **FASE 9: Integración con GPT personalizado de OpenAI**

- Creación y edición de archivo `openapi.yaml` con especificación 3.1.0
- Los archivos `openapi.yaml` y `ai-plugin.json` se colocan en `static/` y se sirven desde FastAPI en `/openapi.yaml` y `/.well-known/ai-plugin.json`.
- Configuración de túnel público con `ngrok`

- Automatización:

    - Nuevo `run.py` inicia Weaviate con Docker Compose y arranca la API. Ejecutar `python run.py` para poner ambos servicios en marcha.
        
- Validación de la función `queryLegal` desde GPT personalizado
    
- Confirmación de conexión y estructura de respuesta funcional
    

---

### **FASE 10: Servidor persistente del LLM**

- Ejecución de `llama-cpp.server` en puerto alternativo (`8001`)
    
- Adaptación de `llm_local.py` para conectarse vía `model_url`
    
- Reducción significativa del tiempo de respuesta
    
- Confirmación de que LangChain funciona con el modelo ya cargado en memoria
    

---

### **FASE 11: Preparación para múltiples GPTs / Conjuntos de conocimiento**

- Inclusión de parámetro `gpt_id` en:
    
    - `query_generator.py`
        
    - `query_retriever.py`
        
    - API REST (`QueryRequest`)
        
- Creación del diccionario `GPT_PROFILES` que permite configurar:
    
    - Clase de Weaviate asociada (`class_name`)
        
    - Prompt especializado
        
- Lógica modular en `get_rag_chain()` y `get_retriever()` para aplicar el `gpt_id`
    
- Preparación para asignar distintos subconjuntos documentales (por clase o metadatos)
    
- Simulación de estructura futura para múltiples GPTs (`legal`, `laboral`, etc.)
    

---

### **FASE 12: Ajuste fino del chunking y reinicio limpio del sistema**

- Cambio de `chunk_size` a 300 y `chunk_overlap` a 30 en `chunk_documents`
- Nuevas variables de entorno `CHUNK_SIZE` y `CHUNK_OVERLAP` para ajustar estos valores
    
- Limpieza completa del entorno:
    
    - Eliminación de `data/chunks/*.txt`
        
    - Eliminación de `.processed_files.json`
        
    - Borrado completo de la clase `LegalDocs` en Weaviate
        
- Reindexación total con los nuevos parámetros:
    
    ```bash
    python scripts/sync_and_index.py --gpt_id default
    ```
    
- Confirmación de regeneración exitosa con chunks más cortos y mejor distribuidos
    

---

### **FASE 13: Preparación para reindexado automático y gestión de cambios**

- Creación del script `sync_and_index.py`:
    
    - Detecta nuevos documentos en `data/raw`
        
    - Evita duplicación de archivos ya procesados
        
    - Vuelve a trocear y reindexar solo lo nuevo
        
 - Control mediante archivo `.processed_files.json` (ahora registra el hash del
   documento y si ha sido troceado e indexado para evitar reprocesos)
 - Parametrización por `--gpt_id` para clasificar por GPT
 - Se calcula un hash por archivo para detectar cambios y evitar reindexados innecesarios
 - Listo para ejecución manual o futura automatización por `cron` / `Task Scheduler`
    
#### limpieza y reindexación
```
(venv) PS C:\Users\ramon\Desktop\RAG_asistente> del data\chunks\*.txt (venv) PS C:\Users\ramon\Desktop\RAG_asistente> python scripts/delete_class.py Clase 'LegalDocs' eliminada de Weaviate. (venv) PS C:\Users\ramon\Desktop\RAG_asistente> del data\.processed_files.json (venv) PS C:\Users\ramon\Desktop\RAG_asistente> python scripts/sync_and_index.py --gpt_id default
```
### **FASE 14: Sincronización opcional con OneDrive**

- Creación del módulo `src/ingestion/onedrive_client.py` para autenticar y descargar documentos.
- Nuevas variables de entorno en `settings.py`:
  - `ONEDRIVE_CLIENT_ID`, `ONEDRIVE_CLIENT_SECRET`, `ONEDRIVE_TENANT_ID`
  - `ONEDRIVE_DRIVE_ID`, `ONEDRIVE_FOLDER`
  - `USE_ONEDRIVE` y `ENTRYPOINT_URL`
  - `ONEDRIVE_MAX_RETRIES`, `ONEDRIVE_RETRY_DELAY`
  - `USE_ONEDRIVE` es `false` por defecto; cámbialo a `true` para sincronizar documentos desde OneDrive
  - `process_documents` ahora, si `USE_ONEDRIVE=true`, lee los archivos directamente desde OneDrive sin guardarlos en `data/raw` y genera los chunks en `data/chunks`.
  - Además acepta un parámetro opcional `tracker` para omitir los ficheros locales ya procesados y evitar leerlos de nuevo.
  - Para usar esta modalidad remota se debe configurar el `.env` con las credenciales anteriores. El cliente cuenta con un método `iter_files()` que devuelve `(nombre, id, modificado, bytes)` para cada documento y, opcionalmente, recorre subcarpetas con `recursive=True`.
  - Se añade un ejemplo de configuración en `*.env.example`.
  - Nuevo script `scripts/check_onedrive.py` para verificar la conectividad listando el contenido de la ruta configurada.
  - Nuevos parámetros `ONEDRIVE_MAX_RETRIES` y `ONEDRIVE_RETRY_DELAY` controlan los reintentos automáticos en las operaciones del cliente mostrando mensajes en consola cuando ocurren.


---

### **FASE 15: Optimización y transición a Weaviate v4**

- Refactor completo de los scripts para el cliente `weaviate-client` 4.x usando `connect_to_custom`.
- Definición del puerto gRPC (`50051`) y cierre explícito de las conexiones.
- `embedder.py` crea las colecciones con `vectorizer_config=Configure.Vectorizer.none()` y añade textos mediante `WeaviateVectorStore`.
- `retriever_module.py`, `index_chunks.py` y `sync_and_index.py` se adaptan a la nueva API.
- Mejora del script `run.py` para lanzar Weaviate y la API comprobando puertos libres y mostrando mensajes de estado.
- Actualización de utilidades (`delete_class.py`, `list_embeddings.py`, `show_classes.py`) para listar y gestionar colecciones con la nueva sintaxis.


### **FASE 16: Supervisión automática de servicios**

- Se añaden archivos `services/rag_watchdog.service` y `services/rag_watchdog.timer` para monitorizar la API y Weaviate.
- Para activarlo en sistemas con `systemd`:
  ```bash
  sudo systemctl enable --now rag_watchdog.timer
  ```
---

### **FASE 17: Scripts de arranque y vigilancia**

- `start_server.sh` inicia la API en segundo plano y guarda los mensajes en `rag_api.log`.
  ```bash
  bash start_server.sh
  ```
- `stop_api.sh` detiene de forma limpia cualquier proceso `run.py` que esté en ejecución.
  ```bash
  bash stop_api.sh
  ```
- `watch_services.sh` comprueba periódicamente que Weaviate y la API sigan activos y los reinicie si se detienen.
  ```bash
  bash watch_services.sh
  ```
  Estos scripts pueden programarse mediante `cron` o integrarse con `systemd` para supervisión automática.


### **Configuraci\u00f3n del archivo .env**

La ra\u00edz del proyecto contiene un archivo `.env.example` con todas las variables de entorno disponibles:

- `OPENAI_API_KEY` - clave para la API de OpenAI.
- `OPENAI_MODEL_NAME` - modelo de OpenAI a utilizar.
- `WEAVIATE_URL` - URL del servidor Weaviate.
- `WEAVIATE_API_KEY` - clave de autenticaci\u00f3n para Weaviate.
- `USE_LOCAL_LLM` - permite usar un LLM local en lugar de la API de OpenAI.
- `LLM_MODEL_PATH` - ruta al modelo local en formato GGUF.
- `LLM_MODEL_URL` - URL del servidor del modelo local.
- `EMBEDDING_DEVICE` - dispositivo (`cpu` o `cuda`) para generar embeddings.
- `ONEDRIVE_PATH` - directorio base para sincronizar con OneDrive.
- `ONEDRIVE_CLIENT_ID` - identificador de la aplicaci\u00f3n en OneDrive.
- `ONEDRIVE_CLIENT_SECRET` - secreto de la aplicaci\u00f3n.
- `ONEDRIVE_TENANT_ID` - tenant de Azure asociado.
- `ONEDRIVE_DRIVE_ID` - unidad de OneDrive a usar.
- `ONEDRIVE_FOLDER` - carpeta remota con los documentos.
- `USE_ONEDRIVE` - habilita la descarga desde OneDrive.
- `ENTRYPOINT_URL` - URL p\u00fablica donde se expone la API.
- `ONEDRIVE_MAX_RETRIES` - n\u00famero de reintentos ante fallos.
- `ONEDRIVE_RETRY_DELAY` - pausa en segundos entre reintentos.
- `DATA_RAW_PATH` - ruta de documentos originales.
- `DATA_CHUNKS_PATH` - ruta donde se guardan los chunks procesados.
- `DATA_INDEX_PATH` - ruta del \u00edndice local.
- `USE_MOCK_MODE` - simula respuestas sin consultar el LLM.
- `DEBUG_PRINT_CONTEXT` - muestra en consola el contexto enviado al modelo.
- `API_KEY` - clave para proteger el endpoint REST.
- `DOCS_INPUT_PATH` - ruta de entrada para los documentos.
- `DOCS_OUTPUT_PATH` - ruta de salida para los chunks.
- `CHUNK_SIZE` - tama\u00f1o de cada fragmento.
- `CHUNK_OVERLAP` - solapamiento entre fragmentos.
- `MAX_CONTEXT_TOKENS` - l\u00edmite de tokens de contexto.
- `MAX_COMPLETION_TOKENS` - l\u00edmite de tokens generados por respuesta.
- `RETRIEVER_K` - cantidad de documentos que recupera el buscador.
- `BATCH_SIZE` - controla el tama\u00f1o de lote para generar embeddings.
- `API_PORT` - puerto usado por el servidor FastAPI.
- `API_WORKERS` - n\u00famero de procesos Uvicorn al ejecutar `start_api.py`.
- `COMPOSE_FILE` - ruta personalizada para `docker-compose.yml`.


