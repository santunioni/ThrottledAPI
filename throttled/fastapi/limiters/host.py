from starlette.requests import Request

from throttled.limiter import Limiter

from ..base import Middleware


class HostBasedLimiter(Limiter, Middleware):
    def _maybe_block_request(self, request: Request):
        self(request)

    def __call__(self, request: Request):  # pylint: disable=arguments-differ
        self.limit(key=f"host={request.client.host}")
