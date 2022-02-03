from starlette.requests import Request

from ..base import FastAPIRequestLimiter


class TotalLimiter(FastAPIRequestLimiter):
    def __call__(self, request: Request):
        self.limit(key="total")
