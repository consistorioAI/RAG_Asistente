from pydantic import BaseModel
from typing import Optional, List, Dict 

class QueryRequest(BaseModel):
    question: str
    gpt_id: Optional[str] = "default"  # ← clave para selección de colección

class SourceDocument(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
