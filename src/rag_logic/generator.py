from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.documents import Document
from src.rag_logic.retriever_module import get_retriever
from src.rag_logic.llm_local import get_local_llm
from src.config.gpt_profiles import GPT_PROFILES
from transformers import BertTokenizer
from langchain.prompts import PromptTemplate


# Tokenizer para estimar tamaño de contexto
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def estimate_tokens(text: str) -> int:
    return len(tokenizer.encode(text, truncation=False))

def filter_docs_by_token_limit(docs, max_tokens: int = 3000):
    total = 0
    selected = []
    for doc in docs:
        tokens = estimate_tokens(doc.page_content)
        if total + tokens > max_tokens:
            break
        selected.append(doc)
        total += tokens
    return selected


def get_rag_chain(gpt_id: str = "default", k: int = 5):
    profile = GPT_PROFILES.get(gpt_id, GPT_PROFILES["default"])

    # Recuperador
    retriever = get_retriever(k=k, collection_name=profile["collection"])

    # LLM local
    llm = get_local_llm()

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
        docs = filter_docs_by_token_limit(docs, max_tokens=3000)

        return combine_chain.run({
            "input_documents": docs,
            "question": question
        })

    return run_rag
