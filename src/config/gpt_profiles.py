# src/config/gpt_profiles.py

from langchain.prompts import PromptTemplate

GPT_PROFILES = {

    # Define aquí los perfiles de GPT que usarás en tu aplicación
    # Cada perfil debe tener un nombre único y puede incluir una colección de documentos
    "default": {
        "collection": "LegalDocs_default",
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""
Actúa como Consultor GPT, especialista en contratación pública local. 
Responde de forma jurídica, precisa y profesional usando solo la información de ConsistorioAI y su conector. 

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
        )
    },
    "contratacion": {
        "collection": "LegalDocs_contratacion",
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""
Actúa como asesor experto en contratación pública.
Responde de forma jurídica y precisa utilizando únicamente la información
proporcionada en la base de conocimiento.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
        )
    },


    "consultor": {
        "collection": "LegalDocs_consultor",
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""
Eres un consultor jurídico especializado en derecho administrativo.
Responde de forma clara y concisa utilizando únicamente la información proporcionada.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
        )
    },
}
