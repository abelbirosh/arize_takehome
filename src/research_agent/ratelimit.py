"""Per-model request throttle, shared across threads.

New OpenRouter accounts are capped at 20 requests/minute per model; a benchmark
grid with many concurrent agents blows through that instantly.
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque

_DEFAULT_RPM = int(os.environ.get("MODEL_RPM", "18"))


class _Window:
    def __init__(self, rpm: int):
        self.rpm = rpm
        self.calls: deque[float] = deque()
        self.lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                while self.calls and now - self.calls[0] >= 60:
                    self.calls.popleft()
                if len(self.calls) < self.rpm:
                    self.calls.append(now)
                    return
                wait = 60 - (now - self.calls[0]) + 0.05
            time.sleep(wait)


_windows: dict[str, _Window] = defaultdict(lambda: _Window(_DEFAULT_RPM))
_guard = threading.Lock()
_local = threading.local()


def throttle(model: str) -> None:
    """Block until another request to `model` fits in its one-minute window.

    Time spent waiting is tallied per thread, so latency metrics can exclude it:
    under a shared rate limit, queueing says nothing about the model.
    """
    with _guard:
        window = _windows[model]
    t0 = time.monotonic()
    window.acquire()
    _local.waited = getattr(_local, "waited", 0.0) + (time.monotonic() - t0)


def reset_wait() -> None:
    _local.waited = 0.0


def waited_ms() -> float:
    return getattr(_local, "waited", 0.0) * 1000
