import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = max(limit, 1)
        self.window = max(window_seconds, 1)
        self._hits: Dict[int, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, user_id: int) -> Tuple[bool, int]:
        now = time.monotonic()
        async with self._lock:
            dq = self._hits[user_id]
            while dq and now - dq[0] > self.window:
                dq.popleft()
            if len(dq) >= self.limit:
                retry_after = int(self.window - (now - dq[0])) + 1
                return False, max(retry_after, 1)
            dq.append(now)
            return True, 0

    async def reset(self, user_id: int) -> None:
        async with self._lock:
            self._hits.pop(user_id, None)
