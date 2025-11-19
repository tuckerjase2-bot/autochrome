# googygoogy — Chromium automation (Playwright)

This small project provides a local Flask UI to build and run Chromium automation plans using Playwright.

Files created:
- `main.py` — Flask UI and API endpoints (`/`, `/run`, `/status`, `/generate`).
- `automator.py` — Automation engine that executes plans via Playwright.
- `gpt_builder.py` — Placeholder GPT helper (uses a placeholder key/endpoint).
- `templates/index.html` — Simple web UI for building plans and invoking runs.
- `install_dependencies.ps1` — PowerShell script to create a venv and install dependencies + Playwright browsers.
- `.env.example` — Example environment variables (place your API key here).

Quick start (PowerShell)

```powershell
cd C:\Users\tucke\googygoogy
.\install_dependencies.ps1
# Activate the venv:
. .\.venv\Scripts\Activate.ps1
# Run the UI server:
python main.py
```

Open a browser at `http://localhost:8080/` to edit a plan and run it.

Notes
- The GPT integration is a placeholder. Put your API key into a `.env` file (copy `.env.example`) and set `OPENAI_API_KEY`.
 - The GPT integration reads your system-wide env var `dOPENAI_KEY_LOL` by default. As a fallback it will also check `OPENAI_API_KEY`.
	 Copy `.env.example` to `.env` and set `dOPENAI_KEY_LOL=YOUR_API_KEY_HERE`.
- The `install_dependencies.ps1` script runs `playwright install chromium` so browsers will be available.
- Plan format: JSON with a top-level `steps` list. Each step is an object with `action` and related fields. See the example in the UI.

Security
- Keep your API keys out of source control. Use environment variables or a local `.env` file (not committed).

If you want, I can:
- Initialize a Git repo and make an initial commit.
- Add authentication to the UI.
- Add more action types or richer variable support.
