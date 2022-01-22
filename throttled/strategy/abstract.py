from abc import ABC, abstractmethod

from throttled import Hit


class Strategy(ABC):
    @abstractmethod
    def __call__(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """
