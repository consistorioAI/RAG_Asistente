from weaviate import connect_to_custom

client = connect_to_custom(
    "127.0.0.1",      # http_host
    8080,             # http_port
    False,            # http_secure
    "127.0.0.1",      # grpc_host
    50051,            # grpc_port
    True,            # grpc_secure (cámbialo a True para la prueba TLS)
)
client.connect()
print("Conexión gRPC OK")
