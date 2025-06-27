import sys, traceback
from pathlib import Path

# Añade root del proyecto al PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.ingestion.onedrive_client import OneDriveClient


def main():
    print("\n=== DEBUG check_onedrive.py ===")
    print("CLIENT_ID :", settings.ONEDRIVE_CLIENT_ID[:8], "…")
    print("TENANT_ID :", settings.ONEDRIVE_TENANT_ID)
    print("DRIVE_ID  :", settings.ONEDRIVE_DRIVE_ID)
    print("FOLDER    :", settings.ONEDRIVE_FOLDER or "/")
    print("----------------------------------------------------\n")

    # 1️⃣ Validar variables de entorno
    required = [
        settings.ONEDRIVE_CLIENT_ID,
        settings.ONEDRIVE_CLIENT_SECRET,
        settings.ONEDRIVE_TENANT_ID,
        settings.ONEDRIVE_DRIVE_ID,
    ]
    if not all(required):
        print("❌  Faltan variables de entorno necesarias.")
        return

    try:
        # 2️⃣ Crear cliente y obtener token
        client = OneDriveClient(
            settings.ONEDRIVE_CLIENT_ID,
            settings.ONEDRIVE_CLIENT_SECRET,
            settings.ONEDRIVE_TENANT_ID,
        )

        # 3️⃣ Listar archivos
        print(f"\n🌐  Listando '{settings.ONEDRIVE_FOLDER or '/'}' …")
        files = client.list_files(
            settings.ONEDRIVE_DRIVE_ID, settings.ONEDRIVE_FOLDER
        )
        print(f"✅  Graph devolvió {len(files)} ítems\n")

    except Exception:
        print("❌  Se produjo una excepción:")
        traceback.print_exc()
        return

    # 4️⃣ Mostrar resultado
    folder = settings.ONEDRIVE_FOLDER or "/"
    print(f"📂  Archivos en '{folder}':")
    for item in files:
        if "file" in item:
            print(f"   - {item['name']}")


if __name__ == "__main__":
    main()
