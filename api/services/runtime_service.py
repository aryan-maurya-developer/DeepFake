from __future__ import annotations

from typing import Any


def get_runtime_profile() -> dict[str, Any]:
    profile = {
        "processing_mode": "CPU-only",
        "gpu_available": False,
        "gpu_name": None,
        "torch_available": False,
    }
    try:
        import torch

        profile["torch_available"] = True
        if torch.cuda.is_available():
            profile["gpu_available"] = True
            profile["processing_mode"] = "GPU-accelerated"
            profile["gpu_name"] = torch.cuda.get_device_name(0)
    except Exception:
        pass
    return profile
