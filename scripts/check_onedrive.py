import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.ingestion.onedrive_client import OneDriveClient


def main():
    if not all([
        settings.ONEDRIVE_CLIENT_ID,
        settings.ONEDRIVE_CLIENT_SECRET,
        settings.ONEDRIVE_TENANT_ID,
        settings.ONEDRIVE_DRIVE_ID,
    ]):
        print("Faltan variables de entorno de OneDrive.")
        return

    try:
        client = OneDriveClient(
            settings.ONEDRIVE_CLIENT_ID,
            settings.ONEDRIVE_CLIENT_SECRET,
            settings.ONEDRIVE_TENANT_ID,
        )
        files = client.list_files(settings.ONEDRIVE_DRIVE_ID, settings.ONEDRIVE_FOLDER)
    except Exception as e:
        print(f"Error al conectar con OneDrive: {e}")
        return

    folder = settings.ONEDRIVE_FOLDER or "/"
    print(f"Archivos en '{folder}':")
    for item in files:
        if "file" in item:
            print(f"- {item['name']}")


if __name__ == "__main__":
    main()
