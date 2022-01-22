from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, NamedTuple

from throttled import Hit, Rate
from throttled.exceptions import RateLimitExceeded


class Strategy(ABC):
    @abstractmethod
    def __call__(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """


class HitsWindow(NamedTuple):
    initialized_at: float
    hits: Deque[Hit]


class FixedWindowStrategy(Strategy):
    def __init__(self, limit: Rate):
        self.__limit = limit
        self.__initialized_at = 0
        self.__hits = deque()

    def __get_time_spent_in_window(self, hit: Hit) -> float:
        return hit.time % self.__limit.interval

    def __maybe_reset(self, hit: Hit):
        initialized_at = hit.time - self.__get_time_spent_in_window(hit)
        if initialized_at > self.__initialized_at:
            self.__hits = deque()
            self.__initialized_at = initialized_at

    def __call__(self, hit: Hit):
        self.__maybe_reset(hit)
        rate = Rate.from_hits(self.__hits)
        if rate > self.__limit:
            raise RateLimitExceeded(
                "global",
                retry_after=int(
                    self.__limit.interval - self.__get_time_spent_in_window(hit)
                ),
            )
        self.__hits.append(hit)
