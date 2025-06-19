from langchain.chains import RetrievalQA
# from langchain.chat_models import ChatOpenAI
from src.rag_logic.retriever_module import get_retriever
from src.rag_logic.llm_local import get_local_llm
from src.config import settings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

def get_rag_chain(k: int = 5, use_local: bool = None):
    retriever = get_retriever(k=k)

    if use_local is None:
        use_local = settings.USE_LOCAL_LLM

    if use_local:
        llm = get_local_llm()
    else:
        # Producción (GPT)
        # llm = ChatOpenAI(
        #     model="gpt-3.5-turbo",
        #     temperature=0,
        #     openai_api_key=settings.OPENAI_API_KEY,
        #     max_tokens=1024
        # )
        raise NotImplementedError("OpenAI desactivado en modo pruebas")

    # NUEVO PROMPT EN ESPAÑOL
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Responde en español, de forma clara y profesional.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return chain

