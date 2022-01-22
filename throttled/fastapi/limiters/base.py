from abc import ABC, abstractmethod
from typing import Callable

from starlette import status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from throttled.exceptions import RateLimitExceeded
from throttled.strategy import Strategy


def response_from_exception(exc: RateLimitExceeded) -> Response:
    return Response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=f"Rate exceeded for key={exc.key}.",
        headers={"Retry-After": str(exc.retry_after)},
    )


async def catcher_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except RateLimitExceeded as exc:
        return response_from_exception(exc)


class Middleware(ABC):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            self._maybe_block_request(request)
            return await call_next(request)
        except RateLimitExceeded as exc:
            return response_from_exception(exc)

    @abstractmethod
    def _maybe_block_request(self, request: Request):
        ...


class Limiter(Callable, ABC):
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def __call__(self, *args, **kwargs):
        ...
