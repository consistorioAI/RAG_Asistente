import json
import time
from pathlib import Path
import requests
from requests.exceptions import RequestException
from msal import ConfidentialClientApplication, SerializableTokenCache
from src.config import settings


class OneDriveClient:
    """Cliente para acceder a OneDrive vía Microsoft Graph (flujo client-credentials)."""

    def __init__(self, client_id: str, client_secret: str, tenant_id: str,
                 max_retries: int | None = None, retry_delay: float | None = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.max_retries = max_retries if max_retries is not None else settings.ONEDRIVE_MAX_RETRIES
        self.retry_delay = retry_delay if retry_delay is not None else settings.ONEDRIVE_RETRY_DELAY

        # ---- MSAL application & token cache ----
        cache = SerializableTokenCache()
        self._app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            token_cache=cache,
        )

        self._token: dict | None = None
        self._token_exp: float = 0.0

    # ---------- Autenticación -------------------------------------------------
    def _authenticate(self) -> dict:
        for attempt in range(1, self.max_retries + 1):
            msg = f"🔐  Autenticando con MSAL (intento {attempt}/{self.max_retries})…"
            print(msg)
            try:
                result = self._app.acquire_token_for_client(scopes=self.scopes)
                print("   Resultado token:", json.dumps(result, indent=2)[:400], "…")
            except Exception as e:
                print(f"   ❌  Error: {e}")
                if attempt == self.max_retries:
                    raise
                print(f"   ↻  Reintentando en {self.retry_delay}s…")
                time.sleep(self.retry_delay)
                continue

            if "access_token" in result:
                print("✅  Token OK, expira en:", result.get("expires_in"), "seg")
                return result

            err = result.get("error_description", "sin descripción")
            print(f"   ❌  Autenticación fallida: {err}")
            if attempt == self.max_retries:
                raise RuntimeError(f"Autenticación fallida: {err}")
            print(f"   ↻  Reintentando en {self.retry_delay}s…")
            time.sleep(self.retry_delay)

        raise RuntimeError("Autenticación fallida tras reintentos")

    def _get_token(self) -> str:
        """Devuelve un access-token válido refrescándolo si es necesario."""
        if time.time() > self._token_exp - 300:
            token_info = self._authenticate()
            self._token = token_info["access_token"]
            self._token_exp = time.time() + token_info.get("expires_in", 0)
        return self._token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._get_token()}"}

    # ---------- Operaciones de ficheros --------------------------------------
    def list_files(self, drive_id: str, folder_path: str):
        """Lista los elementos de la carpeta."""
        url = f"{self.base_url}/drives/{drive_id}/root:/{folder_path}:/children"
        headers = self._headers()

        for attempt in range(1, self.max_retries + 1):
            print(f"🌐  GET {url} (intento {attempt}/{self.max_retries})")
            try:
                resp = requests.get(url, headers=headers)
            except RequestException as e:
                print(f"   ❌  Error de conexión: {e}")
                if attempt == self.max_retries:
                    raise
                print(f"   ↻  Reintentando en {self.retry_delay}s…")
                time.sleep(self.retry_delay)
                continue

            print("   → Status", resp.status_code)

            if resp.status_code == 200:
                return resp.json().get("value", [])

            if resp.status_code >= 500:
                print("   ❌  Error del servidor")
                if attempt == self.max_retries:
                    resp.raise_for_status()
                print(f"   ↻  Reintentando en {self.retry_delay}s…")
                time.sleep(self.retry_delay)
                continue

            print("   ❌  Cuerpo:", resp.text[:500])
            resp.raise_for_status()

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

            for attempt in range(1, self.max_retries + 1):
                print(f"⬇️  Descargando {filename} (intento {attempt}/{self.max_retries})")
                try:
                    file_resp = requests.get(download_url)
                except RequestException as e:
                    print(f"   ❌  Error de conexión: {e}")
                    if attempt == self.max_retries:
                        raise
                    print(f"   ↻  Reintentando en {self.retry_delay}s…")
                    time.sleep(self.retry_delay)
                    continue

                if file_resp.status_code >= 500:
                    print(f"   ❌  Status {file_resp.status_code}")
                    if attempt == self.max_retries:
                        file_resp.raise_for_status()
                    print(f"   ↻  Reintentando en {self.retry_delay}s…")
                    time.sleep(self.retry_delay)
                    continue

                file_resp.raise_for_status()
                (dest_dir / filename).write_bytes(file_resp.content)
                break

    def get_file_bytes(self, drive_id: str, item_id: str) -> bytes:
        """Obtiene el contenido binario de un archivo dado su item_id."""
        url = f"{self.base_url}/drives/{drive_id}/items/{item_id}/content"
        headers = self._headers()
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(url, headers=headers)
            except RequestException as e:
                print(f"   ❌  Error de conexión: {e}")
                if attempt == self.max_retries:
                    raise
                print(f"   ↻  Reintentando en {self.retry_delay}s…")
                time.sleep(self.retry_delay)
                continue

            if resp.status_code >= 500:
                print(f"   ❌  Status {resp.status_code}")
                if attempt == self.max_retries:
                    resp.raise_for_status()
                print(f"   ↻  Reintentando en {self.retry_delay}s…")
                time.sleep(self.retry_delay)
                continue

            resp.raise_for_status()
            return resp.content

    def iter_files(self, drive_id: str, folder_path: str, recursive: bool = False):
        """Iterador que devuelve (nombre, id, fecha_mod, bytes).

        Si ``recursive`` es ``True`` también recorre subcarpetas de forma
        recursiva siguiendo una búsqueda en profundidad.
        """
        for item in self.list_files(drive_id, folder_path):
            if "file" in item:
                yield (
                    item["name"],
                    item["id"],
                    item.get("lastModifiedDateTime"),
                    self.get_file_bytes(drive_id, item["id"]),
                )
            elif recursive and "folder" in item:
                sub_path = f"{folder_path}/{item['name']}".strip("/")
                yield from self.iter_files(drive_id, sub_path, recursive=True)
