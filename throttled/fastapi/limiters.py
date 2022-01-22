from collections import deque

from cachetools import TTLCache

from throttled import Hit, Rate


class TooManyHits(Exception):
    ...


class SimpleLimiter:
    def __init__(self, limit: Rate):
        self.__limit = limit
        self.__cache = TTLCache(maxsize=2, ttl=self.__limit.interval)

    def __call__(self):
        hit = Hit(key="global")
        key = f"{hit.key}:{hit.time // self.__limit.interval}"
        hits = self.__cache.get(key)
        if hits is None:
            hits = deque()
            self.__cache[key] = hits
        rate = Rate.from_hits(hits)
        if rate > self.__limit:
            raise TooManyHits
        hits.append(hit)
