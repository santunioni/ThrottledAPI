from typing import List, Sequence, Union

from fastapi import Depends, FastAPI
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
    def dependencies(self) -> Sequence[Depends]:
        return tuple(Depends(limiter) for limiter in self.__dependency_limiters)

    @property
    def middlewares(self) -> Sequence[DispatchFunction]:
        funcs = [catcher_middleware]
        for limiter in self.__middleware_limiters:
            funcs.append(limiter.dispatch)
        return funcs

    def inject_middlewares_in_app(self, app: FastAPI):
        for middleware in self.middlewares:
            app.add_middleware(BaseHTTPMiddleware, dispatch=middleware)
