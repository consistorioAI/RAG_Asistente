from langchain.chains import RetrievalQA
# from langchain.chat_models import ChatOpenAI
from src.rag_logic.retriever_module import get_retriever
from src.rag_logic.llm_local import get_local_llm
from src.config import settings
from langchain.prompts import PromptTemplate
from src.config.gpt_profiles import GPT_PROFILES



def get_rag_chain(gpt_id: str = "default", k: int = 5):
    profile = GPT_PROFILES.get(gpt_id, GPT_PROFILES["default"])
    
    retriever = get_retriever(k=k, collection_name=profile["collection"])
    
    chain = RetrievalQA.from_chain_type(
        llm=get_local_llm(),
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt": profile["prompt"]} if profile["prompt"] else {}
    )

    return chain

