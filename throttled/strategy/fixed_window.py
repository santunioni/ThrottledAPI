from collections import deque
from typing import Deque, MutableMapping, NamedTuple, Optional

from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit, Rate
from throttled.strategy.abstract import Strategy


class HitsWindow(NamedTuple):
    initialized_at: float
    hits: Deque[Hit]


class FixedWindowStrategy(Strategy):
    def __init__(
        self, limit: Rate, cache: Optional[MutableMapping[str, HitsWindow]] = None
    ):
        self.__limit = limit
        self.__cache: MutableMapping[str, HitsWindow] = cache or {}

    def __get_time_spent_in_window(self, hit: Hit) -> float:
        return hit.time % self.__limit.interval

    def __maybe_reset(self, hit: Hit):
        initialized_at = hit.time - self.__get_time_spent_in_window(hit)

        if hit.key not in self.__cache:
            self.__cache[hit.key] = HitsWindow(initialized_at, deque())
            return

        window = self.__cache[hit.key]
        if initialized_at > window.initialized_at:
            self.__cache[hit.key] = HitsWindow(initialized_at, deque())

    def maybe_block(self, hit: Hit):
        self.__maybe_reset(hit)
        window = self.__cache[hit.key]
        if len(window.hits) >= self.__limit.hits:
            raise RateLimitExceeded(
                hit.key,
                retry_after=int(
                    self.__limit.interval - self.__get_time_spent_in_window(hit)
                ),
            )
        window.hits.append(hit)
