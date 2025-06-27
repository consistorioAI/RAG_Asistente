import json
from pathlib import Path
import requests
from msal import ConfidentialClientApplication


class OneDriveClient:
    """Cliente para acceder a OneDrive vía Microsoft Graph (flujo client-credentials)."""

    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.base_url = "https://graph.microsoft.com/v1.0"

        # Guarda el dict completo con metadatos y el access_token por separado
        self.token_info = self._authenticate()
        self.token = self.token_info["access_token"]

    # ---------- Autenticación -------------------------------------------------
    def _authenticate(self) -> dict:
        print("🔐  Autenticando con MSAL...")
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
        )

        result = app.acquire_token_for_client(scopes=self.scopes)
        print("   Resultado token:", json.dumps(result, indent=2)[:400], "…")

        if "access_token" not in result:
            err = result.get("error_description", "sin descripción")
            raise RuntimeError(f"Autenticación fallida: {err}")

        print("✅  Token OK, expira en:", result.get("expires_in"), "seg")
        return result

    # ---------- Operaciones de ficheros --------------------------------------
    def list_files(self, drive_id: str, folder_path: str):
        """Lista los elementos de la carpeta."""
        url = f"{self.base_url}/drives/{drive_id}/root:/{folder_path}:/children"
        headers = {"Authorization": f"Bearer {self.token}"}

        print(f"🌐  GET {url}")
        resp = requests.get(url, headers=headers)
        print("   → Status", resp.status_code)

        if resp.status_code != 200:
            print("   ❌  Cuerpo:", resp.text[:500])
            resp.raise_for_status()

        return resp.json().get("value", [])

    def download_folder(self, drive_id: str, folder_path: str, dest_dir: Path):
        """Descarga todos los archivos de la carpeta en dest_dir."""
        items = self.list_files(drive_id, folder_path)
        dest_dir.mkdir(parents=True, exist_ok=True)

        for item in items:
            if "file" not in item:
                continue  # salta subcarpetas
            download_url = item.get("@microsoft.graph.downloadUrl")
            if not download_url:
                continue
            filename = item["name"]
            print(f"⬇️  Descargando {filename} ...")
            file_resp = requests.get(download_url)
            file_resp.raise_for_status()
            (dest_dir / filename).write_bytes(file_resp.content)

    def get_file_bytes(self, drive_id: str, item_id: str) -> bytes:
        """Obtiene el contenido binario de un archivo dado su item_id."""
        url = f"{self.base_url}/drives/{drive_id}/items/{item_id}/content"
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.content

    def iter_files(self, drive_id: str, folder_path: str):
        """Iterador que devuelve (nombre, id, fecha_mod, bytes)."""
        for item in self.list_files(drive_id, folder_path):
            if "file" not in item:
                continue
            yield (
                item["name"],
                item["id"],
                item.get("lastModifiedDateTime"),
                self.get_file_bytes(drive_id, item["id"]),
            )
