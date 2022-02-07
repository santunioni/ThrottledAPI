from abc import ABC, abstractmethod

from throttled.exceptions import RateLimitExceeded
from throttled.models import Hit, Rate
from throttled.storage.base import Storage


class StorageFactory(ABC):
    @abstractmethod
    def get_storage_for_strategy(self, strategy: "Strategy", limit: Rate) -> Storage:
        ...


class Strategy:
    __slots__ = ("__limit", "__storage")

    def __init__(self, limit: Rate, storage_factory: StorageFactory):
        self.__limit = limit
        self.__storage = storage_factory.get_storage_for_strategy(self, limit)

    def maybe_block(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """
        window = self.__storage.get_current_window(hit)
        if window.incr(hit.cost) > self.__limit.hits:
            raise RateLimitExceeded(
                hit.key,
                retry_after=window.get_remaining_seconds(),
            )
