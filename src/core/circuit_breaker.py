import asyncio
from collections.abc import Awaitable, Callable
from enum import StrEnum
from time import monotonic
from typing import TypeVar


T = TypeVar("T")


class CircuitState(StrEnum):
    closed = "closed"
    open = "open"
    half_open = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_seconds: float = 30.0) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.state = CircuitState.closed
        self.opened_at = 0.0
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        async with self._lock:
            if self.state == CircuitState.open:
                if monotonic() - self.opened_at < self.recovery_seconds:
                    raise RuntimeError("circuit breaker is open")
                self.state = CircuitState.half_open
        try:
            result = await func()
        except Exception:
            async with self._lock:
                self.failures += 1
                if self.failures >= self.failure_threshold:
                    self.state = CircuitState.open
                    self.opened_at = monotonic()
            raise
        async with self._lock:
            self.failures = 0
            self.state = CircuitState.closed
        return result

