from starlette.requests import Request

from ..base import FastAPIRequestLimiter


class HostBasedLimiter(FastAPIRequestLimiter):
    def __call__(self, request: Request):
        self.limit(key=f"host={request.client.host}")
