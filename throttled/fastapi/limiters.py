from collections import deque
from typing import Optional

from cachetools import TTLCache

from throttled import Hit, Rate


class RateLimitExceeded(Exception):
    def __init__(self, key: str, retry_after: Optional[int] = None):
        self.key = key
        self.retry_after = retry_after


class SimpleLimiter:
    def __init__(self, limit: Rate):
        self.__limit = limit
        self.__cache = TTLCache(maxsize=2, ttl=self.__limit.interval)

    def __call__(self):
        hit = Hit(key="global")
        counter_initialized = int((hit.time // self.__limit.interval) * hit.time)
        key = f"{hit.key}:{counter_initialized}"
        hits = self.__cache.get(key)
        if hits is None:
            hits = deque()
            self.__cache[key] = hits
        rate = Rate.from_hits(hits)
        if rate > self.__limit:
            raise RateLimitExceeded(
                key,
                retry_after=int(
                    self.__limit.interval - (hit.time - counter_initialized)
                ),
            )
        hits.append(hit)
