from __future__ import annotations

import hashlib
import threading
import time
from typing import Any

from settings import settings


class TTLCache:
    def __init__(self, ttl_seconds: int, max_items: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._lock = threading.Lock()
        self._store: dict[str, tuple[float, Any]] = {}

    def _cleanup(self) -> None:
        now = time.time()
        expired = [key for key, (ts, _) in self._store.items() if now - ts > self.ttl_seconds]
        for key in expired:
            self._store.pop(key, None)
        if len(self._store) > self.max_items:
            oldest_keys = sorted(self._store.items(), key=lambda item: item[1][0])[
                : len(self._store) - self.max_items
            ]
            for key, _ in oldest_keys:
                self._store.pop(key, None)

    def get(self, key: str) -> Any | None:
        with self._lock:
            self._cleanup()
            item = self._store.get(key)
            return item[1] if item else None

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cleanup()
            self._store[key] = (time.time(), value)


def build_cache_key(*parts: Any) -> str:
    digest = hashlib.sha256()
    for part in parts:
        if isinstance(part, bytes):
            digest.update(part)
        else:
            digest.update(str(part).encode("utf-8"))
    return digest.hexdigest()


analysis_cache = TTLCache(
    ttl_seconds=settings.cache_ttl_seconds,
    max_items=settings.cache_max_items,
)
