from __future__ import annotations

import random
import time
from typing import (
    Awaitable,
    Callable,
    Iterable,
    Optional,
    TypeVar,
)

T = TypeVar("T")
CallableT = Callable[..., T]
CallableAwaitableT = Callable[..., Awaitable[T]]
RetryDecorator = Callable[[CallableT], CallableT]
RetryAsyncDecorator = Callable[[CallableAwaitableT], CallableAwaitableT]


class CircuitBreaker:
    """
    Simple circuit breaker.

    - opens after `failure_threshold` consecutive failures
    - stays open for `reset_timeout_sec`
    - half-open allows a single trial; success closes, failure re-opens
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout_sec: int = 30,
    ):
        self.failure_threshold = max(1, failure_threshold)
        self.reset_timeout_sec = max(1, reset_timeout_sec)
        self._consecutive_failures = 0
        self._state = "closed"  # closed | open | half-open
        self._open_until: Optional[float] = None

    def allow(self) -> bool:
        if self._state == "closed":
            return True
        now = time.time()
        if (
            self._state == "open"
            and self._open_until
            and now >= self._open_until
        ):
            # Move to half-open for a trial
            self._state = "half-open"
            return True
        return self._state == "half-open"

    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._state = "closed"
        self._open_until = None

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._state = "open"
            self._open_until = time.time() + self.reset_timeout_sec


def _compute_backoff(
    base: float,
    factor: float,
    attempt: int,
    jitter: float,
) -> float:
    delay = base * (factor ** max(0, attempt - 1))
    if jitter > 0:
        delay += random.uniform(0, jitter)
    return delay


def retry(
    exceptions: Iterable[type[BaseException]] = (Exception,),
    max_attempts: int = 3,
    base_delay: float = 0.2,
    factor: float = 2.0,
    jitter: float = 0.1,
) -> RetryDecorator:
    """Synchronous retry decorator with exponential backoff and jitter."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            attempt = 1
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:  # type: ignore
                    if attempt >= max_attempts:
                        raise
                    time.sleep(
                        _compute_backoff(base_delay, factor, attempt, jitter)
                    )
                    attempt += 1

        return wrapper

    return decorator


def async_retry(
    exceptions: Iterable[type[BaseException]] = (Exception,),
    max_attempts: int = 3,
    base_delay: float = 0.2,
    factor: float = 2.0,
    jitter: float = 0.1,
) -> RetryAsyncDecorator:
    """Async retry decorator with exponential backoff and jitter."""
    import asyncio

    def decorator(fn: CallableAwaitableT) -> CallableAwaitableT:
        async def wrapper(*args, **kwargs) -> T:
            attempt = 1
            while True:
                try:
                    return await fn(*args, **kwargs)
                except exceptions:  # type: ignore
                    if attempt >= max_attempts:
                        raise
                    await asyncio.sleep(
                        _compute_backoff(base_delay, factor, attempt, jitter)
                    )
                    attempt += 1

        return wrapper

    return decorator
