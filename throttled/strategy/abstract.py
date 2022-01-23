from abc import ABC, abstractmethod

from throttled.models import Hit


class Strategy(ABC):
    @abstractmethod
    def maybe_block(self, hit: Hit):
        """
        :param hit: The hit to be tested
        :raises: RateLimitExceeded
        """
