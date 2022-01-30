from abc import ABC, abstractmethod

from throttled.models import Hit


class HitsWindow:
    @abstractmethod
    def get_remaining_seconds(self) -> int:
        ...

    @abstractmethod
    def incr(self, hits: int = 1) -> int:
        ...


class Storage(ABC):
    @abstractmethod
    def get_current_window(self, hit: Hit) -> HitsWindow:
        ...
