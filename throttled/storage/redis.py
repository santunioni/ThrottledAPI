"""
This module defines redis storage for WindowManager's
"""

from redis.client import Redis

from throttled.models import Hit, Rate
from throttled.storage import BaseStorage
from throttled.storage._abstract import _HitsWindow, _WindowManager
from throttled.storage._duration import DUR_REGISTRY, DurationCalcType
from throttled.strategies import Strategies


class _RedisWindow(_HitsWindow):
    __slots__ = ("__client", "__interval", "__hit", "__duration_func")

    def __init__(
        self, interval: float, client: Redis, hit: Hit, duration_func: DurationCalcType
    ):
        self.__client = client
        self.__interval = interval
        self.__duration_func = duration_func
        self.__hit = hit

    def incr(self, hits: int = 1) -> int:
        value = self.__client.incrby(name=self.__hit.key, amount=hits)
        if value == hits:
            self.__client.pexpire(
                name=self.__hit.key,
                time=int(self.__duration_func(self.__hit.time, self.__interval) * 1e3),
            )
        return value

    def get_remaining_seconds(self) -> float:
        return self.__client.pttl(name=self.__hit.key) * 1e-3


class _RedisWindowManager(_WindowManager):
    __slots__ = ("__interval", "__client", "__duration_func")

    def __init__(self, interval: float, client: Redis, duration_func: DurationCalcType):
        self.__client = client
        self.__interval = interval
        self.__duration_func = duration_func

    def get_current_window(self, hit: Hit) -> _RedisWindow:
        return _RedisWindow(
            client=self.__client,
            interval=self.__interval,
            hit=hit,
            duration_func=self.__duration_func,
        )


class RedisStorage(BaseStorage):
    def __init__(
        self,
        client: Redis,
    ):
        self.__client = client

    def get_window_manager(
        self, strategy: Strategies, limit: Rate
    ) -> _RedisWindowManager:
        return _RedisWindowManager(
            interval=limit.interval,
            duration_func=DUR_REGISTRY[strategy],
            client=self.__client,
        )


__all__ = ["RedisStorage"]
