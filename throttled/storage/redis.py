from redis.client import Redis

from throttled.models import Hit, Rate
from throttled.storage._duration_funcs import DURATION_FUNCTIONS, DurationCalcType
from throttled.storage.abstract import HitsWindow, WindowManager
from throttled.strategy.base import Storage, Strategy


class _RedisWindow(HitsWindow):
    __slots__ = ("__client", "__interval", "__key", "__duration_calc")

    def __init__(
        self, client: Redis, interval: int, hit: Hit, duration_func: DurationCalcType
    ):
        self.__client = client
        self.__interval = interval
        self.__hit = hit
        self.__duration_func = duration_func
        super().__init__()

    def incr(self, hits: int = 1) -> int:
        value = self.__client.incrby(name=self.__hit.key, amount=hits)
        if value == hits:
            self.__client.pexpire(
                name=self.__hit.key,
                time=int(1000 * self.__duration_func(self.__hit.time, self.__interval)),
            )
        return value

    def decr(self, hits: int = 1) -> int:
        value = self.__client.decrby(name=self.__hit.key, amount=hits)
        return value

    def get_remaining_seconds(self) -> float:
        return self.__client.pttl(name=self.__hit.key) / 1000


class _RedisWindowManager(WindowManager):
    __slots__ = ("__interval", "__client", "__duration_calc")

    def __init__(self, interval: int, client: Redis, duration_func: DurationCalcType):
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


class RedisStorage(Storage):
    def __init__(
        self,
        client: Redis,
    ):
        self.__client = client

    def get_window_manager(
        self, strategy: Strategy, limit: Rate
    ) -> _RedisWindowManager:
        return _RedisWindowManager(
            interval=int(limit.interval),
            duration_func=DURATION_FUNCTIONS[strategy.__class__],
            client=self.__client,
        )


__all__ = ["RedisStorage"]
