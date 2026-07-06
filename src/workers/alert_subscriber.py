import asyncio

import redis.asyncio as redis
import structlog

from src.alerts.service import AlertService
from src.config.settings import get_settings

logger = structlog.get_logger(__name__)


async def run_alert_subscriber(stop_event: asyncio.Event) -> None:
    client = redis.from_url(get_settings().redis_url, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe(AlertService.channel)
    try:
        while not stop_event.is_set():
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                logger.warning("alert_received", data=message["data"])
    finally:
        await pubsub.unsubscribe(AlertService.channel)
        await pubsub.aclose()
        await client.aclose()

