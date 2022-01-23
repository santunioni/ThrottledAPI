from typing import List, Union

from fastapi import Depends

from throttled.fastapi.limiters.base import Limiter
from throttled.starlette.builder import StarletteLimiterBuilder
from throttled.starlette.limiters.base import Middleware


class FastAPILimiterBuilder(StarletteLimiterBuilder):
    def __init__(self, use_middleware_where_possible: bool = True):
        self.__dependency_limiters: List[Limiter] = []
        self.__use_middleware_where_possible = use_middleware_where_possible
        super().__init__()

    def append(self, limiter: Union[Limiter, Middleware]):
        if isinstance(limiter, Middleware) and self.__use_middleware_where_possible:
            super().append(limiter)
            return
        if isinstance(limiter, Limiter):
            self.__dependency_limiters.append(limiter)
            return
        raise TypeError(f"Object {limiter} is not a Middleware or Limiter.")

    @property
    def dependencies(self) -> List[Depends]:
        return list(map(Depends, self.__dependency_limiters))
