from __future__ import annotations

import json
import logging
import time
from typing import Any

from database import AnalysisHistory, SessionLocal
from settings import settings

logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient  # type: ignore
    from pymongo.errors import PyMongoError  # type: ignore
except Exception:  # pragma: no cover
    MongoClient = None

    class PyMongoError(Exception):
        pass


class DualPersistenceService:
    def __init__(self) -> None:
        self._mongo_collection = None
        self._mongo_reason = "MongoDB backup is disabled."
        self._initialize_mongo()

    def _initialize_mongo(self) -> None:
        if not settings.mongo_uri:
            self._mongo_reason = "MONGO_URI is not configured."
            return
        if MongoClient is None:
            self._mongo_reason = "pymongo is not installed."
            return
        try:
            client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            self._mongo_collection = client[settings.mongo_db_name][
                settings.mongo_collection_name
            ]
            self._mongo_reason = "connected"
        except Exception as exc:
            logger.warning("MongoDB backup initialization failed: %s", exc)
            self._mongo_reason = str(exc)
            self._mongo_collection = None

    def _save_sqlite(self, record: dict[str, Any]) -> dict[str, Any]:
        session = SessionLocal()
        try:
            history_record = AnalysisHistory(
                request_id=record["request_id"],
                username=record.get("username"),
                media_type=record["media_type"],
                media_name=record.get("media_name"),
                verdict=record["verdict"],
                confidence=float(record.get("confidence", 0.0)),
                ensemble_method=record.get("ensemble_method", "extended"),
                ensemble_score=float(record.get("ensemble_score", 0.0)),
                inference_time=record.get("inference_time"),
                full_response=json.dumps(record.get("full_response", {})),
            )
            session.add(history_record)
            session.commit()
            return {"status": "saved"}
        finally:
            session.close()

    def _save_mongo(self, record: dict[str, Any]) -> dict[str, Any]:
        if self._mongo_collection is None:
            return {"status": "skipped", "reason": self._mongo_reason}
        for attempt in range(3):
            try:
                payload = dict(record)
                payload["saved_at_epoch"] = time.time()
                self._mongo_collection.replace_one(
                    {"request_id": record["request_id"]},
                    payload,
                    upsert=True,
                )
                return {"status": "saved", "attempt": attempt + 1}
            except PyMongoError as exc:
                logger.warning("MongoDB save attempt %s failed for %s: %s", attempt + 1, record["request_id"], exc)
                time.sleep(0.5 * (attempt + 1))
        return {"status": "failed", "reason": "retry_limit_exceeded"}

    def save_analysis(self, record: dict[str, Any]) -> dict[str, Any]:
        sync_status = {"sqlite": {"status": "pending"}, "mongodb": {"status": "pending"}}
        try:
            sync_status["sqlite"] = self._save_sqlite(record)
        except Exception as exc:
            logger.warning("SQLite save failed for %s: %s", record.get("request_id"), exc)
            sync_status["sqlite"] = {"status": "failed", "reason": str(exc)}
        sync_status["mongodb"] = self._save_mongo(record)
        sync_status["verified"] = (
            sync_status["sqlite"].get("status") == "saved"
            and sync_status["mongodb"].get("status") in {"saved", "skipped"}
        )
        return sync_status


dual_persistence_service = DualPersistenceService()
