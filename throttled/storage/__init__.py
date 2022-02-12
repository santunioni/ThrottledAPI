from abc import ABC, abstractmethod

from throttled.models import Rate
from throttled.storage._abstract import _WindowManager
from throttled.strategies import Strategies


class BaseStorage(ABC):
    @abstractmethod
    def get_window_manager(self, strategy: Strategies, limit: Rate) -> _WindowManager:
        """Return a _WindowManager for the given strategy and rate limit."""
