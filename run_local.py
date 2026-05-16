#!/usr/bin/env python3
"""Run the DeepFake platform locally without Docker."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SDK_DIR = ROOT / "sdk"
API_DIR = ROOT / "api"
FRONTEND_DIR = ROOT / "frontend"
LOCAL_CONFIG = ROOT / "config" / "deepfake_config.local.json"


def build_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = [str(ROOT), str(SDK_DIR), str(API_DIR)]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    env.setdefault("DEEPFAKE_CONFIG_FILE_PATH", str(LOCAL_CONFIG))
    env.setdefault("META_MODEL_ARTIFACTS_DIR", str(API_DIR / "meta_model_artifacts"))
    if extra:
        env.update(extra)
    return env


def spawn(command: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.Popen:
    return subprocess.Popen(command, cwd=str(cwd), env=build_env(extra_env))


def ensure_audio_model_repo() -> None:
    repo_dir = ROOT / "models" / "audio" / "vocoder_artifacts" / "temp_repo"
    if repo_dir.exists():
        return
    print("Audio model repository is missing. Attempting to clone it for local execution...")
    subprocess.run(
        [
            "git",
            "clone",
            "https://github.com/csun22/Synthetic-Voice-Detection-Vocoder-Artifacts.git",
            str(repo_dir),
        ],
        cwd=str(ROOT),
        check=False,
    )


def start_models(processes: list[subprocess.Popen]) -> None:
    ensure_audio_model_repo()
    sdk_server = [sys.executable, "-m", "deepfake_sdk.server", "serve"]
    processes.append(
        spawn(sdk_server + ["--manifest", str(ROOT / "models" / "image" / "npr_deepfakedetection" / "model.yaml")], ROOT, {"MODEL_PORT": "5001"})
    )
    processes.append(
        spawn(sdk_server + ["--manifest", str(ROOT / "models" / "image" / "universalfakedetect" / "model.yaml")], ROOT, {"MODEL_PORT": "5004"})
    )
    processes.append(
        spawn(sdk_server + ["--manifest", str(ROOT / "models" / "video" / "cross_efficient_vit" / "model.yaml")], ROOT, {"MODEL_PORT": "7001"})
    )
    processes.append(
        spawn([sys.executable, str(ROOT / "models" / "audio" / "vocoder_artifacts" / "api.py")], ROOT, {"MODEL_PORT": "8001"})
    )


def start_api(processes: list[subprocess.Popen]) -> None:
    processes.append(
        spawn(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000")],
            API_DIR,
        )
    )


def start_frontend(processes: list[subprocess.Popen]) -> None:
    processes.append(spawn(["npm", "start"], FRONTEND_DIR, {"BROWSER": "none"}))


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in reversed(processes):
        if process.poll() is None:
            try:
                process.send_signal(signal.SIGTERM)
            except Exception:
                process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DeepFake locally without Docker.")
    parser.add_argument(
        "--mode",
        choices=["all", "models", "api", "frontend"],
        default="all",
        help="Choose which local services to start.",
    )
    args = parser.parse_args()

    processes: list[subprocess.Popen] = []
    try:
        if args.mode in {"all", "models"}:
            start_models(processes)
            time.sleep(2)
        if args.mode in {"all", "api"}:
            start_api(processes)
        if args.mode in {"all", "frontend"}:
            start_frontend(processes)

        print("DeepFake local services are starting.")
        print("API: http://127.0.0.1:8000")
        print("Frontend: http://127.0.0.1:3000")
        print("Press Ctrl+C to stop all local processes.")
        while True:
            time.sleep(1)
            exited = [proc for proc in processes if proc.poll() is not None]
            if exited:
                return exited[0].returncode or 0
    except KeyboardInterrupt:
        print("Stopping local services...")
        return 0
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
