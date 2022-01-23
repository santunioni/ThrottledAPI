import itertools
from typing import List, Union

from fastapi import Depends
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction

from .limiters.base import Limiter, Middleware, catcher_middleware


class APILimiter:
    def __init__(self, use_middleware_where_possible: bool = True):
        self.__dependency_limiters: List[Limiter] = []
        self.__middleware_limiters: List[Middleware] = []
        self.__use_middleware_where_possible = use_middleware_where_possible

    def append(self, limiter: Union[Limiter, Middleware]):
        if isinstance(limiter, Middleware) and self.__use_middleware_where_possible:
            self.__middleware_limiters.append(limiter)
            return
        if isinstance(limiter, Limiter):
            self.__dependency_limiters.append(limiter)
            return
        raise TypeError(f"Object {limiter} is not a Limiter.")

    @property
    def dependencies(self) -> List[Depends]:
        return list(map(Depends, self.__dependency_limiters))

    @property
    def middlewares(self) -> List[DispatchFunction]:
        return list(itertools.chain((catcher_middleware,), self.__middleware_limiters))

    def inject_middlewares_in_app(self, app: Starlette):
        for middleware in self.middlewares:
            app.add_middleware(BaseHTTPMiddleware, dispatch=middleware)
