from abc import ABC, abstractmethod
from typing import Sequence, Union

from fastapi.exceptions import HTTPException
from starlette import status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from throttled.exceptions import RateLimitExceeded
from throttled.limiter import Limiter
from throttled.strategy.base import Strategy


class HTTPLimitExceeded(HTTPException):
    def __init__(self, exc: RateLimitExceeded):
        self.retry_after = exc.retry_after
        if self.retry_after is None:
            headers = {}
        else:
            headers = {"Retry-After": self.retry_after}
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=exc.detail,
            headers=headers,
        )


def response_from_exception(
    exc: Union[RateLimitExceeded, HTTPLimitExceeded]
) -> Response:
    return Response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=exc.detail,
        headers={"Retry-After": exc.retry_after},
    )


class FastAPILimiter:
    def __init__(self, strategy: Strategy):
        self.__limiter = Limiter(strategy)

    def limit(self, key: str):
        try:
            self.__limiter.limit(key)
        except RateLimitExceeded as exc:
            raise HTTPLimitExceeded(exc) from exc


class FastAPIRequestLimiter(ABC, FastAPILimiter):
    _ignored_paths: Sequence[str] = ("docs", "redoc", "favicon.ico", "openapi.json")

    def __init__(self, strategy: Strategy, response_factory=response_from_exception):
        super().__init__(strategy)
        self.__response_factory = response_factory

    def ignore_path(self, path: str):
        ignored = list(self._ignored_paths)
        ignored.append(path)
        self._ignored_paths = ignored

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            path = str(request.url).replace(str(request.base_url), "")
            if path not in self._ignored_paths:
                self(request)
            return await call_next(request)
        except HTTPLimitExceeded as exc:
            return self.__response_factory(exc)

    @abstractmethod
    def __call__(self, request: Request):
        ...
