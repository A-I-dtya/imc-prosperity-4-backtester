import os
import subprocess
import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.server.shutdown_flag = True
        return super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        return super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return


class CustomHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.shutdown_flag = False

def _is_wsl() -> bool:
    # Check for WSL environment
    if "WSL_DISTRO_NAME" in os.environ:
        return True
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False
    
def _open_url(url: str, force_windows: bool = False) -> None:
    if force_windows or _is_wsl():
        subprocess.run(["powershell.exe", "-NoProfile", "Start-Process", url])
    else:
        webbrowser.open(url)

def open_visualizer(output_file: Path) -> None:
    http_handler = partial(HTTPRequestHandler, directory=str(output_file.parent))
    http_server = CustomHTTPServer(("0.0.0.0", 0), http_handler)

    url = f"http://localhost:{http_server.server_port}/{output_file.name}"
    vis_url = f"https://kevin-fu1.github.io/imc-prosperity-4-visualizer/?open={url}"

    _open_url(vis_url)

    while not http_server.shutdown_flag:
        http_server.handle_request()
