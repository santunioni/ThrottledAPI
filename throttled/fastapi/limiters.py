from starlette.requests import Request

from .base import MiddlewareLimiter


class IPLimiter(MiddlewareLimiter):
    def __call__(self, request: Request):
        host = request.headers.get(
            "X_FORWARDED_FOR", request.client.host or "127.0.0.1"
        )
        self.limit(key=f"host={host}")


class TotalLimiter(MiddlewareLimiter):
    def __call__(self, request: Request):
        self.limit(key="total")
