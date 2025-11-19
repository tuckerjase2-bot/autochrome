#!/usr/bin/env python3
"""Project startup script.

Creates a local virtual environment at `.venv` (if missing), installs requirements,
installs Playwright browsers (Chromium), and launches `main.py` (Flask UI) using
the venv Python interpreter.

Run from PowerShell (project root):

    python start.py

The script is safe to re-run; it will skip steps that are already completed.
"""
import os
import sys
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"


def is_windows() -> bool:
    return sys.platform.startswith("win")


def venv_python() -> Path:
    if is_windows():
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(cmd, **kwargs):
    print("$ ", " ".join(map(str, cmd)))
    return subprocess.run(list(map(str, cmd)), **kwargs)


def ensure_venv():
    if VENV_DIR.exists():
        print(f"Using existing venv at {VENV_DIR}")
        return
    print("Creating virtual environment at .venv...")
    run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def ensure_pip(ven_py: Path):
    print("Upgrading pip in venv...")
    run([str(ven_py), "-m", "pip", "install", "--upgrade", "pip"], check=True)


def install_requirements(ven_py: Path):
    req = ROOT / "requirements.txt"
    if not req.exists():
        print("No requirements.txt found; skipping pip install.")
        return
    print("Installing requirements into venv...")
    run([str(ven_py), "-m", "pip", "install", "-r", str(req)], check=True)


def install_playwright_browsers(ven_py: Path):
    print("Installing Playwright browsers (Chromium)...")
    run([str(ven_py), "-m", "playwright", "install", "chromium"], check=True)


def run_server(ven_py: Path, open_browser: bool = True, host: str = "localhost", port: int = 8080):
    main_py = ROOT / "main.py"
    if not main_py.exists():
        print("Error: main.py not found in project root.")
        sys.exit(1)

    print("Launching Flask server (main.py) using venv Python in background...")
    # Start the server as a background process so we can open the browser.
    proc = subprocess.Popen([str(ven_py), str(main_py)], cwd=str(ROOT))

    # Wait for the server to be reachable on the given host/port (simple TCP connect)
    import socket, time, webbrowser

    deadline = time.time() + 30.0
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                break
        except Exception:
            time.sleep(0.5)

    url = f"http://{host}:{port}/"
    if open_browser:
        try:
            webbrowser.open(url)
            print(f"Opened browser to {url}")
        except Exception:
            print(f"Could not open browser automatically. Visit {url} manually.")

    print("Server process running (press Ctrl+C to stop). Waiting for server to exit...")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("Stopping server...")
        proc.terminate()
        proc.wait()


def main():
    try:
        ensure_venv()
        ven_py = venv_python()
        if not ven_py.exists():
            print("venv python not found where expected; aborting.")
            sys.exit(1)

        ensure_pip(ven_py)
        install_requirements(ven_py)
        # Try to install playwright browsers; it's idempotent
        install_playwright_browsers(ven_py)

        print("Setup complete — starting the app.")
        run_server(ven_py)

    except subprocess.CalledProcessError as e:
        print("A command failed:", e)
        sys.exit(e.returncode if hasattr(e, "returncode") else 1)


if __name__ == "__main__":
    main()
