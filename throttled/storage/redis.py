from typing import Type

from redis.client import Redis

from throttled.models import Hit, Rate
from throttled.storage.abstract import HitsWindow, WindowManager
from throttled.strategy.base import Storage, Strategy


class _RedisWindow(HitsWindow):
    __slots__ = ("__client", "__duration", "__key")

    def __init__(self, client: Redis, duration: int, key: str):
        self.__client = client
        self.__duration = duration
        self.__key = key
        super().__init__()

    def incr(self, hits: int = 1) -> int:
        value = self.__client.incrby(name=self.__key, amount=hits)
        if value == hits:
            self.__client.expire(name=self.__key, time=self.__duration)
        return value

    def decr(self, hits: int = 1) -> int:
        value = self.__client.decrby(name=self.__key, amount=hits)
        return value

    def get_remaining_seconds(self) -> float:
        return self.__client.pttl(name=self.__key) / 1000


class _RedisWindowManager(WindowManager):
    __slots__ = ("__interval", "__client")

    def __init__(
        self,
        interval: int,
        client: Redis,
    ):
        self.__client = client
        self.__interval = interval

    def get_current_window(self, hit: Hit) -> _RedisWindow:
        return _RedisWindow(client=self.__client, duration=self.__interval, key=hit.key)


class RedisStorage(Storage):
    def __init__(
        self,
        client: Redis,
    ):
        self.__client = client

    def get_window_manager(
        self, strategy: Type[Strategy], limit: Rate
    ) -> _RedisWindowManager:
        return _RedisWindowManager(
            interval=int(limit.interval),
            client=self.__client,
        )


__all__ = ["RedisStorage"]
