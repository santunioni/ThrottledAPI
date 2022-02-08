from abc import ABC, abstractmethod

from throttled.models import Hit, Rate


class Storage(ABC):
    @abstractmethod
    def get_window_manager(self, owner: object, limit: Rate) -> "WindowManager":
        ...


class HitsWindow(ABC):
    @abstractmethod
    def get_remaining_seconds(self) -> int:
        ...

    @abstractmethod
    def incr(self, hits: int = 1) -> int:
        ...


class WindowManager(ABC):
    @abstractmethod
    def get_current_window(self, hit: Hit) -> HitsWindow:
        ...
