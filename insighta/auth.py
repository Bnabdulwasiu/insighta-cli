import httpx
import typer
import threading
import webbrowser
import secrets
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from rich.console import Console
# from typer import params

from insighta.api import (
    API_URL, save_credentials, clear_credentials,
    load_credentials, request
)
from insighta.display import print_success, print_error

console = Console()
app = typer.Typer()

# Shared state between server thread and main thread
_callback_result = {}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
            <html><body>
            <h2>Login successful. You can close this tab.</h2>
            </body></html>
        """)

        # ✅ capture tokens from redirect params
        _callback_result["state"] = params.get("state", [None])[0]
        _callback_result["access_token"] = params.get("access_token", [None])[0]
        _callback_result["refresh_token"] = params.get("refresh_token", [None])[0]
        _callback_result["username"] = params.get("username", [None])[0]
        _callback_result["role"] = params.get("role", [None])[0]

    def log_message(self, format, *args):
        pass


def _start_callback_server(port: int):
    server = HTTPServer(("localhost", port), CallbackHandler)
    server.handle_request()  # handle exactly one request then stop

@app.command()
def login():
    """Authenticate with GitHub OAuth."""
    state = secrets.token_urlsafe(16)
    port = 9876
    cli_callback = f"http://localhost:{port}"

    thread = threading.Thread(target=_start_callback_server, args=(port,))
    thread.daemon = True
    thread.start()

    console.print("[cyan]Opening GitHub login in your browser...[/cyan]")

    # ✅ Pass cli_callback so backend knows where to redirect tokens after auth
    params = urlencode({"state": state, "cli_callback": cli_callback})
    webbrowser.open(f"{API_URL}/auth/github?{params}")
    console.print("[dim]Waiting for authentication... (Ctrl+C to cancel)[/dim]")

    try:
        thread.join(timeout=120)
    except KeyboardInterrupt:
        print("\nLogin cancelled.")
        raise typer.Exit(0)

    code = _callback_result.get("code")
    returned_state = _callback_result.get("state")
    access_token = _callback_result.get("access_token")
    refresh_token = _callback_result.get("refresh_token")
    username = _callback_result.get("username")
    role = _callback_result.get("role")

    if not access_token:
        print_error("Login failed — no token received.")
        raise typer.Exit(1)

    if returned_state != state:
        print_error("State mismatch.")
        raise typer.Exit(1)

    save_credentials({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": username,
        "role": role,
    })

    print_success(f"Logged in as @{username}")


@app.command()
def logout():
    """Log out and revoke your session."""
    from insighta.api import get_refresh_token
    refresh = get_refresh_token()
    if refresh:
        try:
            request("POST", "/auth/logout", json={"refresh_token": refresh})
        except SystemExit:
            pass
    clear_credentials()
    print_success("Logged out successfully.")


@app.command()
def whoami():
    """Show currently logged in user."""
    res = request("GET", "/auth/me")
    if res.status_code == 200:
        data = res.json().get("data", {})
        console.print(f"[bold]Username:[/bold] @{data.get('username')}")
        console.print(f"[bold]Role:[/bold]     {data.get('role')}")
        console.print(f"[bold]Email:[/bold]    {data.get('email') or 'N/A'}")
    else:
        print_error(res.json().get("message", "Failed to fetch user."))