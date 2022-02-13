from abc import ABC, abstractmethod
from typing import Callable, Optional, Sequence

from fastapi.exceptions import HTTPException
from starlette import status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from throttled.exceptions import RateLimitExceeded
from throttled.limiter import Limiter
from throttled.models import Rate
from throttled.storage import BaseStorage
from throttled.strategies import Strategies


class HTTPLimitExceeded(HTTPException):
    def __init__(self, exc: RateLimitExceeded, detail: Optional[str] = None):
        self.retry_after = exc.retry_after
        super_kwargs = dict(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": str(round(self.retry_after, 2))},
        )
        if detail is not None:
            super_kwargs["detail"] = detail
        super().__init__(**super_kwargs)


DetailFactory = Callable[[RateLimitExceeded], Optional[str]]


def key_detail_factory(exc: RateLimitExceeded) -> str:
    return f"Rate exceeded for key={exc.key}."


class FastAPILimiter(ABC):
    """First adapter between limiters APIs and FastAPI"""

    def __init__(
        self,
        limit: Rate,
        storage: BaseStorage,
        strategy: Strategies = Strategies.MOVING_WINDOW,
        detail_factory: DetailFactory = key_detail_factory,
    ):
        self.__limiter = Limiter(limit, storage, strategy)
        self.__detail_factory = detail_factory

    def limit(self, key: str):
        """
        Limit the hit based on it's key

        :param key: the key to be limited.
        :raises: HTTPLimitExceeded
        """
        try:
            self.__limiter.limit(key)
        except RateLimitExceeded as exc:
            raise HTTPLimitExceeded(exc, detail=self.__detail_factory(exc)) from exc

    @abstractmethod
    def __call__(self, request: Request):
        """
        This method implementation are supposed to call the limit() method with
        the key to be limited.

        :param request: injected by FastAPI when using the limiter as dependency.
        :raises: HTTPLimitExceeded
        """


ResponseFactory = Callable[[HTTPLimitExceeded], Response]


def default_response_factory(exc: HTTPLimitExceeded) -> Response:
    return Response(
        status_code=exc.status_code,
        headers=exc.headers,
    )


class MiddlewareLimiter(FastAPILimiter, ABC):
    __ignored_paths: Sequence[str] = ("docs", "redoc", "favicon.ico", "openapi.json")

    def __init__(
        self,
        limit: Rate,
        storage: BaseStorage,
        strategy: Strategies = Strategies.MOVING_WINDOW,
        detail_factory: DetailFactory = lambda exc: None,
        response_factory: ResponseFactory = default_response_factory,
    ):
        super().__init__(
            strategy=strategy,
            limit=limit,
            storage=storage,
            detail_factory=detail_factory,
        )
        self.__response_factory = response_factory

    def ignore_path(self, path: str):
        path = path.lstrip("/")
        ignored = list(self.__ignored_paths)
        ignored.append(path)
        self.__ignored_paths = ignored

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Dispatch function which converts the limiter in a Middleware.
        Middlewares are faster because they don't need dependencies to be resolved.

        All limiters that don't use FastAPI dependency injection can be implemented as Middleware.

        :param request: injected by FastAPI when using the limiter as middleware.
        :param call_next: the next middleware from the chain-of-responsibility created by Starlette.
        """
        try:
            path = str(request.url).replace(str(request.base_url), "")
            if path not in self.__ignored_paths:
                self(request)
            return await call_next(request)
        except HTTPLimitExceeded as exc:
            return self.__response_factory(exc)
