from typing import List

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction

from throttled.starlette.limiters.base import Middleware, catcher_middleware


class StarletteLimiterBuilder:
    def __init__(self) -> None:
        self.__middleware_limiters: List[Middleware] = []

    def append(self, limiter: Middleware):
        if not isinstance(limiter, Middleware):
            raise TypeError(f"Object {limiter} is not a Middleware.")
        self.__middleware_limiters.append(limiter)

    @property
    def middlewares(self) -> List[DispatchFunction]:
        funcs = [catcher_middleware]
        for limiter in self.__middleware_limiters:
            funcs.append(limiter.dispatch)
        return funcs

    def inject_middlewares_in_app(self, app: Starlette):
        for middleware in self.middlewares:
            app.add_middleware(BaseHTTPMiddleware, dispatch=middleware)
