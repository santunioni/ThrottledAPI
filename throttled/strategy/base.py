from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit, Rate
from throttled.storage.abstract import Storage


class Strategy:
    __slots__ = ("__limit", "__window_manager")

    def __init__(self, limit: Rate, storage: Storage):
        self.__limit = limit
        self.__window_manager = storage.get_window_manager(
            owner=self.__class__, limit=limit
        )

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
