from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.concurrency import run_in_threadpool
from src.api.schemas import QueryRequest, QueryResponse, SourceDocument
from src.rag_logic.generator import get_rag_chain
from fastapi import Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import traceback

from src.config import settings  # <-- importar configuración del .env

app = FastAPI(title="RAG API", description="API de consulta semántica legal", version="0.1.0")
ALLOWED_ORIGINS = ["https://chatgpt.com"]  # o añade tu dominio de front-end

# Permitir el acceso a la API desde cualquier origen para que la 
# documentación interactiva funcione correctamente cuando se accede 
# de forma remota.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


def verify_api_key(
    x_api_key: str = Header(
        None, alias="X-API-Key", convert_underscores=False   # alias explícito
    )
):
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, valid: bool = Depends(verify_api_key)):
    if settings.USE_MOCK_MODE:
        print(f"[MOCK] Recibida pregunta: {request.question}")
        return QueryResponse(
            answer="(Simulación) El sistema ha recibido tu pregunta y funcionaría correctamente.",
            sources=[
                SourceDocument(
                    content="(Documento simulado) Este sería un fragmento relevante del corpus legal.",
                    metadata={"simulado": True, "documento": "ejemplo.txt"}
                )
            ]
        )

    try:
        
        chain = get_rag_chain(gpt_id=request.gpt_id, k=settings.RETRIEVER_K)
        result = await run_in_threadpool(chain, request.question)

        sources = [
            SourceDocument(
                content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in result["source_documents"]
        ]

        return QueryResponse(
            answer=result["result"],
            sources=sources
        )

    except Exception as e:
        print("ERROR en /query:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al procesar la consulta: {str(e)}")

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def ai_plugin():
    return FileResponse("static/ai-plugin.json", media_type="application/json")


@app.get("/openapi.yaml", include_in_schema=False)
async def openapi_yaml():
    return FileResponse("static/openapi.yaml", media_type="text/yaml")

