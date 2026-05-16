$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r api\requirements.txt

Push-Location frontend
npm install
Pop-Location

Write-Host "Local environment ready. Run .\start.bat to launch the stack."
