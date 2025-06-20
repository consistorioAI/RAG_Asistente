from fastapi import FastAPI, HTTPException
from src.api.schemas import QueryRequest, QueryResponse, SourceDocument
from src.rag_logic.generator import get_rag_chain
from fastapi.responses import FileResponse
from pathlib import Path
import traceback

from src.config import settings  # <-- importar configuración del .env

app = FastAPI(title="RAG API", description="API de consulta semántica legal", version="0.1.0")

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
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
        chain = get_rag_chain(k=5)
        result = chain(request.question)

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

@app.get("/openapi.yaml")
def serve_openapi_spec():
    openapi_path = Path(__file__).resolve().parent.parent.parent / "openapi.yaml"
    return FileResponse(openapi_path, media_type="text/yaml")
