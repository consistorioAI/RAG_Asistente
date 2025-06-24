import weaviate
from weaviate.auth import AuthApiKey

client = weaviate.Client(
    url="http://localhost:8080",
    #auth_client_secret=AuthApiKey(api_key="clave_super_secreta")  # usa el mismo valor de .env
)

print(client.is_ready())  # ✅ Esto debe devolver True
