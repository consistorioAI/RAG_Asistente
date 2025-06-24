import requests
from pathlib import Path
from msal import ConfidentialClientApplication


class OneDriveClient:
    """Cliente sencillo para descargar archivos desde OneDrive usando Microsoft Graph."""

    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = self._authenticate()

    def _authenticate(self) -> str:
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
        result = app.acquire_token_for_client(scopes=self.scopes)
        if "access_token" not in result:
            raise RuntimeError(f"Autenticación fallida: {result.get('error_description')}")
        return result["access_token"]

    def download_folder(self, drive_id: str, folder_path: str, dest_dir: Path):
        """Descarga todos los archivos del folder indicado en dest_dir."""
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/drives/{drive_id}/root:/{folder_path}:/children"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        items = response.json().get("value", [])
        dest_dir.mkdir(parents=True, exist_ok=True)

        for item in items:
            if "file" not in item:
                continue
            download_url = item.get("@microsoft.graph.downloadUrl")
            if not download_url:
                continue
            filename = item["name"]
            file_resp = requests.get(download_url)
            file_resp.raise_for_status()
            with open(dest_dir / filename, "wb") as f:
                f.write(file_resp.content)

    def list_files(self, drive_id: str, folder_path: str):
        """Devuelve la lista de archivos en un directorio de OneDrive."""
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/drives/{drive_id}/root:/{folder_path}:/children"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("value", [])

    def get_file_bytes(self, drive_id: str, item_id: str) -> bytes:
        """Obtiene el contenido binario de un archivo por item_id."""
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/drives/{drive_id}/items/{item_id}/content"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content

    def iter_files(self, drive_id: str, folder_path: str):
        """Itera sobre los archivos del folder y devuelve (nombre, bytes)."""
        for item in self.list_files(drive_id, folder_path):
            if "file" not in item:
                continue
            data = self.get_file_bytes(drive_id, item["id"])
            yield item["name"], data

