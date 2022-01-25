from starlette.requests import Request

from throttled.limiter import Limiter

from ..base import Middleware


class TotalLimiter(Limiter, Middleware):
    def _maybe_block_request(self, request: Request):
        self()

    def __call__(self):
        self.limit(key="total")
