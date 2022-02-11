from starlette.requests import Request

from ..base import MiddlewareLimiter


class TotalLimiter(MiddlewareLimiter):
    def __call__(self, request: Request):
        self.limit(key="total")
