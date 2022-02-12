import asyncio
import functools
from typing import Any, Callable, TypeVar, cast

from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit, Rate
from throttled.storage import BaseStorage
from throttled.strategies import Strategies

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


class Limiter:
    __slots__ = ("__limit", "__window_manager")

    def __init__(
        self,
        limit: Rate,
        storage: BaseStorage,
        strategy: Strategies,
    ):
        self.__limit = limit
        self.__window_manager = storage.get_window_manager(
            strategy=strategy, limit=limit
        )

    def __maybe_block(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """
        window = self.__window_manager.get_current_window(hit)
        if window.incr(hit.cost) > self.__limit.hits:
            raise RateLimitExceeded(
                hit.key,
                retry_after=window.get_remaining_seconds(),
            )

    def limit(self, key: str):
        self.__maybe_block(Hit(key=key))

    def decorate(self, func: FuncT) -> FuncT:
        key = f"func={func.__name__}:hash={hash(func)}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.limit(key)
            return func(*args, **kwargs)

        @functools.wraps(func)
        async def a_wrapper(*args, **kwargs):
            self.limit(key)
            return await func(*args, **kwargs)

        return cast(FuncT, a_wrapper if asyncio.iscoroutinefunction(func) else wrapper)
