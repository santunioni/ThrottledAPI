from typing import Callable, Tuple, Type

from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from throttled.fastapi.limiters import RateLimitExceeded

ExceptionType = Type[Exception]
HandlerType = Callable[[Request, Exception], Response]

FastAPIHandler = Tuple[ExceptionType, HandlerType]


def handle_rate_exceed_func(request: Request, exc: RateLimitExceeded) -> Response:
    return Response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=f"Rate exceeded for key={exc.key}.",
    )


handle_rate_exceed: FastAPIHandler = (RateLimitExceeded, handle_rate_exceed_func)
