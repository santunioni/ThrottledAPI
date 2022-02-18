from abc import ABC, abstractmethod

from throttled.models import Hit


class _HitsWindow(ABC):
    @abstractmethod
    def get_remaining_seconds(self) -> float:
        """Get the time (seconds) in which this HitsWindow will expire."""

    @abstractmethod
    def incr(self, hits: int = 1) -> int:
        """
        Increase the hit count in this window

        :param hits: the number of hits to increase in the window
        :return: the current hits number, after increased
        """

    def is_expired(self) -> bool:
        """
        Check if this window already expired

        :return: boolean True if the window already expired, False otherwise
        """
        return self.get_remaining_seconds() <= 0


class _WindowManager(ABC):
    @abstractmethod
    def get_current_window(self, hit: Hit) -> _HitsWindow:
        """
        Get the current active HitsWindow

        :param hit: hit to get the HitsWindow for
        :return: the currently active HitsWindow instance
        """
