from starlette.requests import Request

from throttled import Hit
from throttled.fastapi.limiters.base import Limiter
from throttled.starlette.limiters.base import Middleware


class HostBasedLimiter(Limiter, Middleware):
    def _maybe_block_request(self, request: Request):
        self(request)

    def __call__(self, request: Request):  # pylint: disable=arguments-differ
        hit = Hit(key=f"host={request.client.host}")
        self._strategy(hit)
