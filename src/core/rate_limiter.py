import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from src.config.settings import get_settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def __call__(self, request: Request) -> None:
        settings = get_settings()
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window_start = now - 60
        hits = self._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= settings.rate_limit_per_minute:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
        hits.append(now)


rate_limiter = InMemoryRateLimiter()

