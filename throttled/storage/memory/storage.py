from typing import Callable, Mapping, MutableMapping, Type

from throttled.models import Hit
from throttled.storage.base import Storage
from throttled.storage.memory.window import MemoryWindow
from throttled.strategy import FixedWindowStrategy, MovingWindowStrategy
from throttled.strategy.base import Strategy


def _fixed_window_duration_calc(hit_time: float, interval: float) -> float:
    return hit_time - hit_time % interval + interval


def _moving_window_duration_calc(_: float, interval: float) -> float:
    return interval


_DurationCalcType = Callable[[float, float], float]
DURATION_CALC: Mapping[Type[Strategy], _DurationCalcType] = {
    FixedWindowStrategy: _fixed_window_duration_calc,
    MovingWindowStrategy: _moving_window_duration_calc,
}


class MemoryStorage(Storage):
    __slots__ = ("__interval", "__cache", "__duration_calc")

    def __init__(self, interval: float, duration_calc: _DurationCalcType):
        self.__cache: MutableMapping[str, MemoryWindow] = {}
        self.__interval = interval
        self.__duration_calc = duration_calc

    def get_current_window(self, hit: Hit) -> MemoryWindow:
        window = self.__cache.get(hit.key)
        if window is None or window.get_remaining_seconds() < 0:
            self.__cache[hit.key] = window = MemoryWindow(
                duration=self.__duration_calc(hit.time, self.__interval)
            )
        return window
