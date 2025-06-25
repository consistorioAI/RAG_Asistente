from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from src.rag_logic.retriever_module import get_retriever
from src.rag_logic.llm_local import get_local_llm
from src.config.gpt_profiles import GPT_PROFILES
from transformers import BertTokenizer
from langchain.prompts import PromptTemplate
from src.config import settings
from src.rag_logic.llm_openai import get_openai_llm
from functools import lru_cache


# Tokenizer para estimar tamaño de contexto
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def estimate_tokens(text: str) -> int:
    return len(tokenizer.encode(text, truncation=False))

def truncate_text(text: str, max_tokens: int) -> str:
    tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)


def filter_docs_by_token_limit(docs, max_tokens: int = settings.MAX_CONTEXT_TOKENS):
    """Limita el contexto total a un máximo de tokens."""
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

    # Recuperador
    retriever = get_retriever(k=k, collection_name=profile["collection"])

    # LLM local
    llm = get_local_llm() if settings.USE_LOCAL_LLM else get_openai_llm()

    # Prompt
    prompt = profile["prompt"] or PromptTemplate.from_template("Contexto:\n{context}\n\nPregunta: {question}\n\nRespuesta:")

    # LLMChain para aplicar el prompt
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )

    # Combinador de documentos (stuff)
    combine_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context"  # debe coincidir con el nombre usado en prompt.input_variables
    )

    def run_rag(question: str):
        docs = retriever.get_relevant_documents(question)
        docs = filter_docs_by_token_limit(docs, max_tokens=settings.MAX_CONTEXT_TOKENS)

        if settings.DEBUG_PRINT_CONTEXT:
            print("\n[DEBUG] Contexto recuperado:")
            for i, doc in enumerate(docs, 1):
                print(f"\n--- Documento {i} ---")
                print(doc.page_content)
                print("Metadatos:", doc.metadata)

        answer = combine_chain.run({
            "input_documents": docs,
            "question": question
        })

        return {
            "result": answer,
            "source_documents": docs
        }

    return run_rag
