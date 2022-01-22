from typing import Callable, Iterable, List, Union

from fastapi import Depends, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from .limiters.base import Limiter, Middleware, catcher_middleware


def as_dependencies(limiters: Iterable[Callable]) -> List[Depends]:
    return [Depends(limiter) for limiter in limiters]


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

    def instrument(self, app: FastAPI):
        app.router.dependencies.extend(as_dependencies(self.__dependency_limiters))
        app.add_middleware(BaseHTTPMiddleware, dispatch=catcher_middleware)
        for limiter in self.__middleware_limiters:
            app.add_middleware(BaseHTTPMiddleware, dispatch=limiter.dispatch)
