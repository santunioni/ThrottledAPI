from starlette.requests import Request

from throttled import Hit
from throttled.fastapi.limiters.base import Limiter
from throttled.starlette.limiters.base import Middleware


class TotalLimiter(Limiter, Middleware):
    def _maybe_block_request(self, request: Request):
        self()

    def __call__(self):  # pylint: disable=arguments-differ
        self._strategy(Hit(key="total"))
