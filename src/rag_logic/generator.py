from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from src.rag_logic.retriever_module import get_retriever, _create_weaviate_client
from src.rag_logic.llm_local import get_local_llm
from src.config.gpt_profiles import GPT_PROFILES
from transformers import BertTokenizer
from langchain.prompts import PromptTemplate
from src.config import settings
from src.rag_logic.llm_openai import get_openai_llm
from functools import lru_cache
from datetime import datetime
import re

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def estimate_tokens(text: str) -> int:
    return len(tokenizer.encode(text, truncation=False))

def truncate_text(text: str, max_tokens: int) -> str:
    tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)


def score_heuristic(doc: Document, question: str) -> float:
    text = doc.page_content.lower()
    metadata = doc.metadata
    score = 0

    # ✅ 1. Coincidencia léxica simple con la pregunta
    question_terms = set(question.lower().split())
    overlap = sum(1 for word in question_terms if word in text)
    score += min(overlap, 3)  # límite razonable para evitar inflado excesivo

    # ✅ 2. Presencia de identificadores jurídicos
    if "roj" in text or "ecli" in text:
        score += 1

    # ✅ 3. Bonus por actualidad (extrae el año desde el filename)
    filename = metadata.get("filename") or metadata.get("source") or ""
    match = re.search(r"_(\d{4})", filename)
    if match:
        try:
            year = int(match.group(1))
            current_year = datetime.now().year
            years_ago = current_year - year
            score_fecha = max(0, 5 - years_ago)  # +5 si es del año actual, +4 si es del anterior, etc.
            score += score_fecha
        except ValueError:
            pass

    return score


def filter_docs_by_token_limit(docs, question, max_tokens: int = settings.MAX_CONTEXT_TOKENS):
    """Reordena y trunca los documentos más relevantes legalmente."""
    # Ordena por puntuación
    docs = sorted(docs, key=lambda d: score_heuristic(d, question), reverse=True)

    total = 0
    selected = []
    for doc in docs:
        tokens = estimate_tokens(doc.page_content)
        if total + tokens > max_tokens:
            remaining = max_tokens - total
            if remaining <= 0:
                break
            doc.page_content = truncate_text(doc.page_content, remaining)
            selected.append(doc)
            break
        selected.append(doc)
        total += tokens
    return selected


@lru_cache(maxsize=None)
def get_rag_chain(gpt_id: str = "default", k: int = settings.RETRIEVER_K):
    profile = GPT_PROFILES.get(gpt_id, GPT_PROFILES["default"])

    retriever = get_retriever(k=k, collection_name=profile["collection"])
    llm = get_local_llm() if settings.USE_LOCAL_LLM else get_openai_llm()

    prompt = profile["prompt"] or PromptTemplate.from_template("Contexto:\n{context}\n\nPregunta: {question}\n\nRespuesta:")

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    combine_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context"
    )

    def run_rag(question: str):
        nonlocal retriever
        try:
            # 🔄 Cambiado: deprecado get_relevant_documents → invoke
            docs = retriever.invoke(question)
        except Exception:
            _create_weaviate_client.cache_clear()
            retriever = get_retriever(k=k, collection_name=profile["collection"])
            docs = retriever.invoke(question)

        # ✅ Filtrado y priorización avanzada
        docs = filter_docs_by_token_limit(docs, question, max_tokens=settings.MAX_CONTEXT_TOKENS)

        # 👉 Añadir nombre del documento al contexto SOLO si es perfil consultor
        if gpt_id == "consultor":
            for doc in docs:
                filename = doc.metadata.get("filename") or doc.metadata.get("source") or "documento_desconocido"
                header = f"[Documento fuente: {filename.replace('.pdf', '')}]\n"
                doc.page_content = header + doc.page_content

        if settings.DEBUG_PRINT_CONTEXT:
            print("\n[DEBUG] Contexto recuperado:")
            for i, doc in enumerate(docs, 1):
                print(f"\n--- Documento {i} ---")
                print(doc.page_content[:500])
                print("Metadatos:", doc.metadata)

        # Ejecuta la generación
        answer = combine_chain.run({
            "input_documents": docs,
            "question": question
        })

        # 🔽 Ordenar documentos usados por score final
        ranked_sources = sorted(
            docs,
            key=lambda d: score_heuristic(d, question),
            reverse=True
        )

        # 🔖 Formato limpio: extraer nombre del documento sin extensión
        ranked_names = []
        for i, doc in enumerate(ranked_sources[:5], start=1):
            filename = doc.metadata.get("filename") or doc.metadata.get("source") or "documento_desconocido"
            filename_clean = filename.replace(".pdf", "")
            ranked_names.append(f"{i}. {filename_clean}")

        # ➕ Añadir ranking de fuentes al final de la respuesta
        answer += "\n\n**Fuentes utilizadas (ordenadas por relevancia):**\n" + "\n".join(ranked_names)

        return {
            "result": answer,
            "source_documents": docs
        }

    return run_rag
