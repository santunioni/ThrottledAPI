from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit
from throttled.strategy.base import Strategy


class MovingWindowStrategy(Strategy):
    def maybe_block(self, hit: Hit):
        window = self._storage.get_current_window(hit)
        if window.incr(hit.cost) >= self.limit.hits:
            raise RateLimitExceeded(
                hit.key,
                retry_after=window.get_remaining_seconds(),
            )
