# Run from PowerShell in the project root to create venv and install deps
# Usage: .\install_dependencies.ps1

# Create venv
python -m venv .venv

# Upgrade pip and install requirements
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt

# Install Playwright browsers (Chromium)
.\.venv\Scripts\python -m playwright install chromium

Write-Host "Dependencies installed. Activate with: . .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
