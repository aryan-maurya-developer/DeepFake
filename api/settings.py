"""Central runtime settings for the API and local tooling."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


BASE_DIR = Path(__file__).resolve().parent.parent
API_DIR = BASE_DIR / "api"
CONFIG_DIR = BASE_DIR / "config"


@dataclass
class Settings:
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    mongo_uri: str | None = os.getenv("MONGO_URI")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "deepfake_platform")
    mongo_collection_name: str = os.getenv(
        "MONGO_COLLECTION_NAME", "analysis_history"
    )
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "900"))
    cache_max_items: int = int(os.getenv("CACHE_MAX_ITEMS", "256"))
    enable_gpu: bool = os.getenv("USE_GPU", "false").lower() == "true"
    local_model_host: str = os.getenv("LOCAL_MODEL_HOST", "127.0.0.1")
    local_config_path: str = os.getenv(
        "LOCAL_DEEPFAKE_CONFIG_PATH",
        str(CONFIG_DIR / "deepfake_config.local.json"),
    )
    default_config_path: str = os.getenv(
        "DEEPFAKE_CONFIG_FILE_PATH",
        str(CONFIG_DIR / "deepfake_config.json"),
    )
    api_port: int = int(os.getenv("PORT", "8000"))
    frontend_port: int = int(os.getenv("FRONTEND_PORT", "3000"))
    model_ports: Dict[str, int] = field(
        default_factory=lambda: {
            "npr_deepfakedetection": 5001,
            "universalfakedetect": 5004,
            "cross_efficient_vit": 7001,
            "vocoder_artifacts": 8001,
        }
    )


settings = Settings()
