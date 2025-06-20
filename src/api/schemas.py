from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str
    gpt_id: Optional[str] = None  # Preparado para futuro multi-GPT

class SourceDocument(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
