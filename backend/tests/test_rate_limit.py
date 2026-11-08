from app.rate_limit import RateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_allows_up_to_max_then_blocks():
    limiter = RateLimiter(max_attempts=3, window_seconds=60, clock=FakeClock())
    assert [limiter.hit("k") for _ in range(3)] == [None, None, None]
    assert limiter.hit("k") is not None


def test_window_slides_and_allows_again():
    clock = FakeClock()
    limiter = RateLimiter(max_attempts=2, window_seconds=60, clock=clock)
    limiter.hit("k")
    limiter.hit("k")
    assert limiter.hit("k") == 60  # blocked, wait the full window
    clock.now = 61  # jump forward in time, no sleep
    assert limiter.hit("k") is None


def test_keys_are_independent():
    limiter = RateLimiter(max_attempts=1, window_seconds=60, clock=FakeClock())
    assert limiter.hit("a") is None
    assert limiter.hit("b") is None
