from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit, Rate
from throttled.storage import BaseStorage


class Strategy:
    __slots__ = ("__limit", "__window_manager")

    def __init__(self, limit: Rate, storage: BaseStorage):
        self.__limit = limit
        self.__window_manager = storage.get_window_manager(strategy=self, limit=limit)

    def maybe_block(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """
        window = self.__window_manager.get_current_window(hit)
        if window.incr(hit.cost) > self.__limit.hits:
            raise RateLimitExceeded(
                hit.key,
                retry_after=window.get_remaining_seconds(),
            )
