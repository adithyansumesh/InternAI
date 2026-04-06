"""
models/store.py — Hybrid session store for resume data.
Uses Redis for scalable multi-worker persistence in production.
Falls back to an in-memory dictionary if Redis is not installed locally.
"""

import json
from typing import Optional, Dict
from app.models.schemas import ParsedResume
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class ResumeStore:
    def __init__(self):
        self.use_redis = False
        self._local_store: Dict[str, ParsedResume] = {}
        
        try:
            import redis
            self.redis_client = redis.Redis.from_url(
                getattr(settings, 'REDIS_URL', "redis://localhost:6379"),
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Ping to verify Redis is actually running
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Connected to Redis for session storage.")
        except Exception:
            logger.warning("Redis is not running! Falling back to ephemeral in-memory dictionary for local testing.")

    def save(self, resume_id: str, resume: ParsedResume) -> None:
        if self.use_redis:
            try:
                self.redis_client.setex(f"resume:{resume_id}", 86400, resume.model_dump_json())
            except Exception:
                pass
        else:
            self._local_store[resume_id] = resume

    def get(self, resume_id: str) -> Optional[ParsedResume]:
        if self.use_redis:
            try:
                data = self.redis_client.get(f"resume:{resume_id}")
                if data:
                    return ParsedResume.model_validate_json(data)
            except Exception:
                return None
        else:
            return self._local_store.get(resume_id)
        return None

    def exists(self, resume_id: str) -> bool:
        if self.use_redis:
            try:
                return self.redis_client.exists(f"resume:{resume_id}") > 0
            except Exception:
                return False
        return resume_id in self._local_store

    def delete(self, resume_id: str) -> bool:
        if self.use_redis:
            try:
                return self.redis_client.delete(f"resume:{resume_id}") > 0
            except Exception:
                return False
        if resume_id in self._local_store:
            del self._local_store[resume_id]
            return True
        return False

# Global proxy
resume_store = ResumeStore()
