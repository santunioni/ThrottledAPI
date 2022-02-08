from abc import ABC, abstractmethod
from typing import Callable, Optional, Sequence

from fastapi.exceptions import HTTPException
from starlette import status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from throttled.exceptions import RateLimitExceeded
from throttled.limiter import Limiter
from throttled.strategy.base import Strategy

ResponseDetailFactory = Callable[[RateLimitExceeded], Optional[str]]


def key_detail_factory(exc: RateLimitExceeded) -> str:
    return f"Rate exceeded for key={exc.key}."


def null_detail_factory(_: RateLimitExceeded) -> None:
    return None


class HTTPLimitExceeded(HTTPException):
    def __init__(self, exc: RateLimitExceeded, detail: Optional[str] = None):
        self.retry_after = exc.retry_after
        if self.retry_after is None:
            headers = {}
        else:
            headers = {"Retry-After": str(round(self.retry_after))}

        super_kwargs = dict(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, headers=headers
        )
        if detail is not None:
            super_kwargs["detail"] = detail
        super().__init__(**super_kwargs)


class FastAPILimiter:
    """First adapter between limiters APIs and FastAPI"""

    def __init__(
        self,
        strategy: Strategy,
        rdf: ResponseDetailFactory = key_detail_factory,
    ):
        self.__limiter = Limiter(strategy)
        self.__rdf = rdf

    def limit(self, key: str):
        try:
            self.__limiter.limit(key)
        except RateLimitExceeded as exc:
            raise HTTPLimitExceeded(exc, detail=self.__rdf(exc)) from exc


ResponseFactory = Callable[[HTTPLimitExceeded], Response]


def default_response_factory(exc: HTTPLimitExceeded) -> Response:
    return Response(
        status_code=exc.status_code,
        headers=exc.headers,
    )


class FastAPIRequestLimiter(ABC, FastAPILimiter):
    _ignored_paths: Sequence[str] = ("docs", "redoc", "favicon.ico", "openapi.json")

    def __init__(
        self,
        strategy: Strategy,
        response_factory: ResponseFactory = default_response_factory,
    ):
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
