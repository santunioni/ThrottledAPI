from typing import MutableMapping, NamedTuple

from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit, Rate
from throttled.strategy.base import Strategy


class HitsCounter(NamedTuple):
    initialized_at: float
    hits: int


class FixedWindowStrategy(Strategy):
    def __init__(self, limit: Rate):
        self.limit = limit
        self.__cache: MutableMapping[str, HitsCounter] = {}

    def __get_time_spent_in_window(self, hit: Hit) -> float:
        return hit.time % self.limit.interval

    def __maybe_reset(self, hit: Hit):
        initialized_at = hit.time - self.__get_time_spent_in_window(hit)

        if hit.key not in self.__cache:
            self.__cache[hit.key] = HitsCounter(initialized_at, 0)
            return

        window = self.__cache[hit.key]
        if initialized_at > window.initialized_at:
            self.__cache[hit.key] = HitsCounter(initialized_at, 0)

    def maybe_block(self, hit: Hit):
        self.__maybe_reset(hit)
        counter = self.__cache[hit.key]
        if counter.hits >= self.limit.hits:
            raise RateLimitExceeded(
                hit.key,
                retry_after=int(
                    self.limit.interval - self.__get_time_spent_in_window(hit)
                ),
            )
        counter.hits += hit.cost
