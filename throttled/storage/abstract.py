from abc import ABC, abstractmethod

from throttled.models import Hit, Rate


class HitsWindow(ABC):
    @abstractmethod
    def get_remaining_seconds(self) -> int:
        ...

    @abstractmethod
    def incr(self, hits: int = 1) -> int:
        ...

    @abstractmethod
    def decr(self, hits: int = 1) -> int:
        ...

    def is_expired(self) -> bool:
        return self.get_remaining_seconds() <= 0


class WindowManager(ABC):
    @abstractmethod
    def get_current_window(self, hit: Hit) -> HitsWindow:
        ...


class Storage(ABC):
    @abstractmethod
    def get_window_manager(self, strategy: object, limit: Rate) -> WindowManager:
        ...
