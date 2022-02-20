from starlette.requests import Request

from .base import MiddlewareLimiter


class IPLimiter(MiddlewareLimiter):
    def __call__(self, request: Request):
        self.limit(key=f"host={request.client.host}")


class TotalLimiter(MiddlewareLimiter):
    def __call__(self, request: Request):
        self.limit(key="total")
