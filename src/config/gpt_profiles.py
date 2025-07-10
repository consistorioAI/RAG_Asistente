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

    "procesal": {
        "collection": "LegalDocs_procesal",
        "prompt": PromptTemplate(
            input_variables=["context", "question"],
            template="""
Eres un asistente jurídico especializado en derecho procesal.
Extrae los fragmentos relevantes de los documentos y responde de
forma profesional en español.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
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
