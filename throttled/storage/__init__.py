from abc import ABC, abstractmethod

from throttled.models import Rate
from throttled.storage._abstract import _WindowManager


class BaseStorage(ABC):
    @abstractmethod
    def get_window_manager(self, strategy: object, limit: Rate) -> _WindowManager:
        ...
