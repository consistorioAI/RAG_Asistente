# src/config/gpt_profiles.py

from langchain.prompts import PromptTemplate

GPT_PROFILES = {

    # Define aquí los perfiles de GPT que usarás en tu aplicación
    # Cada perfil debe tener un nombre único y puede incluir una colección de documentos
    "default": {
        "collection": "LegalDocs",
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""
Actúa como Consultor GPT, especialista en contratación pública local. 
Responde de forma jurídica, precisa y profesional usando solo la información de ConsistorioAI y su conector. 
Si no puedes verificar una respuesta con estas fuentes, indica claramente: «No puedo verificar esta información». 

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
        )
    },
    "contratos": {
        "collection": "LegalDocs_contratos",
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""
Contesta en tono formal y jurídico, citando fragmentos relevantes.

Contexto legal:
{context}

Pregunta:
{question}

Conclusión:
"""
        )
    },

    # este es un ejemplo de cómo podrías definir un perfil para recursos humanos
    # no es necesario que uses un PromptTemplate específico, puedes dejarlo como None

    "rrhh": {
        "collection": "LegalDocs_rrhh",
        "prompt": None  # Si quisieras usar uno genérico
    }
}
