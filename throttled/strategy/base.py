from abc import ABC, abstractmethod

from throttled.models import Hit, Rate
from throttled.storage.base import Storage


class Strategy(ABC):
    __slots__ = ("__limit", "_storage")

    def __init__(self, limit: Rate, storage_factory: "StorageFactory"):
        self.__limit = limit
        self._storage = storage_factory.get_storage_for_strategy(self)

    @property
    def limit(self) -> Rate:
        return self.__limit

    @abstractmethod
    def maybe_block(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """


class StorageFactory(ABC):
    @abstractmethod
    def get_storage_for_strategy(self, strategy: Strategy) -> Storage:
        ...
