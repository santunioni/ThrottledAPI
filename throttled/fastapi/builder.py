from typing import Any, Callable, List, Union

from fastapi import Depends

from throttled.limiter import Limiter
from throttled.starlette.builder import StarletteLimiterBuilder
from throttled.starlette.limiters.base import Middleware


class FastAPILimiterBuilder(StarletteLimiterBuilder):
    def __init__(self, use_middleware_where_possible: bool = True):
        self.__dependency_limiters: List[Union[Limiter, Callable[..., Any]]] = []
        self.__use_middleware_where_possible = use_middleware_where_possible
        super().__init__()

    def append(self, limiter: Union[Limiter, Middleware]):
        if isinstance(limiter, Middleware) and self.__use_middleware_where_possible:
            super().append(limiter)
        elif isinstance(limiter, Limiter):
            if callable(limiter):
                self.__dependency_limiters.append(limiter)
            else:
                raise TypeError(f"Object {limiter} is not Callable.")
        else:
            raise TypeError(f"Object {limiter} is not a Middleware or Limiter.")

    @property
    def dependencies(self) -> List[Depends]:
        return list(map(Depends, self.__dependency_limiters))
