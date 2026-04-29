import os
import json
import httpx
from pathlib import Path
from typing import Optional

CREDENTIALS_FILE = Path.home() / ".insighta" / "credentials.json"
API_URL = os.getenv("INSIGHTA_API_URL", "https://profile-app-5343e495.fastapicloud.dev")
API_HEADERS = {"X-API-Version": "1"}


def load_credentials() -> dict:
    if not CREDENTIALS_FILE.exists():
        return {}
    with open(CREDENTIALS_FILE) as f:
        return json.load(f)


def save_credentials(data: dict):
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def clear_credentials():
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()


def get_access_token() -> Optional[str]:
    return load_credentials().get("access_token")


def get_refresh_token() -> Optional[str]:
    return load_credentials().get("refresh_token")


def try_refresh() -> bool:
    """Attempt to refresh the access token. Returns True if successful."""
    refresh_token = get_refresh_token()
    if not refresh_token:
        return False

    try:
        res = httpx.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        if res.status_code == 200:
            data = res.json()
            creds = load_credentials()
            creds["access_token"] = data["access_token"]
            creds["refresh_token"] = data["refresh_token"]
            save_credentials(creds)
            return True
    except httpx.RequestError:
        pass
    return False


def request(method: str, path: str, **kwargs) -> httpx.Response:
    """
    Makes an authenticated request.
    Auto-refreshes token on 401 and retries once.
    """
    token = get_access_token()
    if not token:
        from rich.console import Console
        Console().print("[red]Not logged in. Run: insighta login[/red]")
        raise SystemExit(1)

    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    res = httpx.request(method, f"{API_URL}{path}", headers=headers, **kwargs)

    # Token expired — try refresh and retry once
    if res.status_code == 401:
    # Try refresh ONLY if refresh token exists
        if get_refresh_token() and try_refresh():
            token = get_access_token()
            headers["Authorization"] = f"Bearer {token}"
            res = httpx.request(method, f"{API_URL}{path}", headers=headers, **kwargs)
        else:
            from rich.console import Console
            Console().print("[red]Session expired. Run: insighta login[/red]")
            raise SystemExit(1)

    return res