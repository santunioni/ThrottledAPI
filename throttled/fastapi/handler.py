from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from throttled.exceptions import RateLimitExceeded


def handle_rate_exceed_func(_: Request, exc: RateLimitExceeded) -> Response:
    return Response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=f"Rate exceeded for key={exc.key}.",
        headers={"Retry-After": str(exc.retry_after)},
    )


handle_rate_exceed = (RateLimitExceeded, handle_rate_exceed_func)
