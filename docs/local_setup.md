# Local Setup Guide

## What changed

This project can now run without Docker by launching the model services, API gateway, and frontend directly on the host machine.

## Quick start

### Windows

```powershell
.\scripts\setup_local.ps1
.\start.bat
```

### Linux / macOS

```bash
chmod +x scripts/setup_local.sh start.sh
./scripts/setup_local.sh
./start.sh
```

## Manual run

```bash
python run_local.py --mode all
```

Available modes:

- `all`
- `models`
- `api`
- `frontend`

## Runtime notes

- Local API config: `config/deepfake_config.local.json`
- Local API URL: `http://127.0.0.1:8000`
- Local frontend URL: `http://127.0.0.1:3000`
- Mongo backup is optional and enabled through `MONGO_URI`

## New API endpoints

- `POST /detect`
- `POST /analyze/text`
- `POST /analyze/file-safety`
- `POST /analyze/website`
- `GET /health`

## Troubleshooting

- If `npm` is blocked in PowerShell, use `npm.cmd install` and `npm.cmd start`
- If a model fails locally, confirm the weights are present and `PYTHONPATH` includes the repo root plus `sdk`
- The audio model may require the upstream repository clone in `models/audio/vocoder_artifacts/temp_repo` and its pretrained weights in `models/audio/vocoder_artifacts/models/`
- If Mongo sync is skipped, set `MONGO_URI` in `.env`
- If GPU is unavailable, the platform will automatically fall back to CPU mode
