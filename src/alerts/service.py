import json
import time
from typing import Any

import redis.asyncio as redis
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.core.metrics import REDIS_PUBLISH
from src.models.alert import Alert
from src.models.enums import AlertSeverity
from src.repositories.alerts import AlertRepository

logger = structlog.get_logger(__name__)


class AlertService:
    channel = "exchange.alerts"

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db
        self.settings = get_settings()

    async def publish(
        self,
        alert_type: str,
        severity: AlertSeverity,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        body = {
            "type": alert_type,
            "severity": severity.value,
            "message": message,
            "payload": payload or {},
        }
        if self.db:
            await AlertRepository(self.db).add(
                Alert(
                    type=alert_type,
                    severity=severity,
                    message=message,
                    payload=json.dumps(payload or {}),
                )
            )
        start = time.perf_counter()
        client = redis.from_url(self.settings.redis_url, decode_responses=True)
        try:
            await client.publish(self.channel, json.dumps(body))
        except Exception as exc:
            logger.warning("redis_alert_publish_failed", error=str(exc), alert_type=alert_type)
        finally:
            await client.aclose()
            REDIS_PUBLISH.labels(channel=self.channel).observe(time.perf_counter() - start)
