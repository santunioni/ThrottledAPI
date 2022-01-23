import asyncio
import functools
from typing import Any, Callable, TypeVar

from throttled.models import Hit
from throttled.strategy import Strategy

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


class Limiter:
    def __init__(self, strategy: Strategy):
        self.__strategy = strategy

    def limit(self, key: str):
        self.__strategy.maybe_block(Hit(key=key))

    def decorate(self, func: FuncT) -> FuncT:
        key = f"func_name={func.__name__}:func_hash={hash(func)}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.limit(key)
            return func(*args, **kwargs)

        @functools.wraps(func)
        async def a_wrapper(*args, **kwargs):
            self.limit(key)
            return await func(*args, **kwargs)

        return a_wrapper if asyncio.iscoroutinefunction(func) else wrapper
