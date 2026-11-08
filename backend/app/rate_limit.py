import time
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock


class RateLimiter:
    """In-memory sliding-window limiter.

    Good enough for a single process. With several workers/servers the counts
    must live in a shared store (e.g. Redis) instead.
    """

    def __init__(
        self,
        max_attempts: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def hit(self, key: str) -> float | None:
        """Record one attempt for `key`.

        Returns None if allowed, or the number of seconds to wait if blocked.
        """
        now = self._clock()
        with self._lock:
            attempts = self._hits[key]
            # drop attempts that are older than the window
            while attempts and now - attempts[0] >= self.window:
                attempts.popleft()
            if len(attempts) >= self.max_attempts:
                return self.window - (now - attempts[0])
            attempts.append(now)
            return None

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
