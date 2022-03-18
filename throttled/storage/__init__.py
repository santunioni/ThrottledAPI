from abc import ABC, abstractmethod

from throttled.models import Rate
from throttled.storage._abstract import _WindowRepository
from throttled.strategies import Strategies


class BaseStorage(ABC):
    @abstractmethod
    def get_window_repository(
        self, strategy: Strategies, limit: Rate
    ) -> _WindowRepository:
        """Return a _WindowManager for the given strategy and rate limit."""
