# scripts/query_generator.py

import sys
import warnings
import os
from pathlib import Path
from contextlib import redirect_stderr

# Suprimir todos los warnings de Python y LangChain
warnings.filterwarnings("ignore")

# Redirigir stderr a null para ocultar errores técnicos no críticos
null_output = open(os.devnull, 'w')
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
NUM_K = settings.RETRIEVER_K  # Número de documentos a recuperar

from src.rag_logic.generator import get_rag_chain

# if __name__ == "__main__":
#     with redirect_stderr(null_output):
#         print("Generador RAG iniciado. (Ctrl+C para salir).")
#         chain = get_rag_chain(NUM_K)

#         while True:
#             try:
#                 pregunta = input("\nPregunta legal: ")
#                 if not pregunta.strip():
#                     print("Por favor, introduce una pregunta válida.")
#                     continue

#                 result, docs = chain(pregunta)
#                 print(result)
#                 # mostrar fuentes (docs)


#                 print("\nRespuesta generada:")
#                 print(result["result"])

#                 print("\nFuentes utilizadas:")
#                 for i, doc in enumerate(result["source_documents"]):
#                     print(f"\n--- Documento {i+1} ---")
#                     print(doc.page_content[:500], "...")
#                     print("Metadatos:", doc.metadata)

#             except KeyboardInterrupt:
#                 print("\nSesión finalizada por el usuario.")
#                 break
#             except Exception as e:
#                 print(f"\n[Error durante la generación]: {e}")

if __name__ == "__main__":
    print("Generador RAG iniciado. (Ctrl+C para salir).")
    chain = get_rag_chain(k=NUM_K)

    while True:
        pregunta = input("\nPregunta legal: ").strip()
        if pregunta.lower() in {"salir", "exit"}:
            break

        try:
            respuesta = chain(pregunta)
            print("\nRespuesta generada:")
            print(respuesta)
        except Exception as e:
            print(f"\n[Error durante la generación]: {e}")
