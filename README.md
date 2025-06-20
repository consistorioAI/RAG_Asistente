# Log de desarrollo – RAG con GPT y Weaviate
**Fecha de corte: Última integración verificada con GPT personalizado y respuesta simulada vía API**

---

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
    
- Verificación de extracción correcta en entorno local
    

---

### **FASE 3: Chunking, generación de embeddings e indexación**

- División de los documentos en chunks usando `RecursiveCharacterTextSplitter`
    
- Uso de embeddings locales con modelo `sentence-transformers/all-MiniLM-L6-v2`
    
- Downgrade del cliente `weaviate-client` a versión 3.26.7 (por incompatibilidad con LangChain y cliente v4)
    
- Ajustes en el schema de Weaviate:
    
    - Definición de clase `LegalDocs`
        
    - Uso de `vectorizer: none`
        
    - Verificación de existencia de clase usando `client.schema.get()["classes"]`
        
- Indexación exitosa de los vectores en Weaviate vía `langchain_community.vectorstores.Weaviate`
    
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
    

---

### **FASE 9: Integración con GPT personalizado de OpenAI**

- Creación y edición de archivo `openapi.yaml` con especificación 3.1.0
    
- Exposición del archivo en `/openapi.yaml` desde FastAPI
    
- Configuración de túnel público con `ngrok`
    
- Automatización:
    
    - Script `run.py` que lanza ngrok, actualiza el YAML y abre 3 terminales (API, LLM, ngrok)
        
- Validación de la función `queryLegal` desde GPT personalizado
    
- Confirmación de conexión y estructura de respuesta funcional
    

---

### **FASE 10: Servidor persistente del LLM**

- Ejecución de `llama-cpp.server` en puerto alternativo (`8001`)
    
- Adaptación de `llm_local.py` para conectarse vía `model_url`
    
- Reducción significativa del tiempo de respuesta
    
- Confirmación de que LangChain funciona con el modelo ya cargado en memoria
    

---

### **ESTADO ACTUAL DEL PROYECTO**

- Sistema RAG operativo y accesible vía API REST en entorno local
    
- LLM local persistente funcionando en modo servidor
    
- Integrado con GPT personalizado a través de función externa
    
- Capaz de generar respuestas reales o simuladas según configuración
    
- Controlado por variables de entorno portables (`.env`)
    
- Listo para escalabilidad, despliegue futuro en Azure y múltiples GPTs
    
