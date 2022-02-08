import time
from typing import Callable, Mapping, MutableMapping, Optional, Type

from throttled.models import Hit, Rate
from throttled.storage.abstract import HitsWindow, WindowManager
from throttled.strategy import FixedWindowStrategy, MovingWindowStrategy
from throttled.strategy.base import Storage, Strategy


def _fixed_window_duration_calc(hit_time: float, interval: float) -> float:
    return interval - hit_time % interval


def _moving_window_duration_calc(_: float, interval: float) -> float:
    return interval


_DurationCalcType = Callable[[float, float], float]
_DURATION_FUNCTIONS: Mapping[Type[Strategy], _DurationCalcType] = {
    FixedWindowStrategy: _fixed_window_duration_calc,
    MovingWindowStrategy: _moving_window_duration_calc,
}


class MemoryStorage(Storage):
    def __init__(
        self,
        cache: Optional[MutableMapping[str, "_MemoryWindow"]] = None,
    ):
        self.__cache = cache

    def get_window_manager(
        self, owner: Type[Strategy], limit: Rate
    ) -> "_MemoryWindowManager":
        try:
            return _MemoryWindowManager(
                interval=limit.interval,
                duration_func=_DURATION_FUNCTIONS[owner],
                cache=self.__cache,
            )
        except KeyError as err:
            raise TypeError(
                f"There is not MemoryStorage for strategy {owner} implemented yet!"
            ) from err


class _MemoryWindowManager(WindowManager):
    __slots__ = ("__interval", "__cache", "__duration_calc")

    def __init__(
        self,
        interval: float,
        duration_func: _DurationCalcType,
        cache: Optional[MutableMapping[str, "_MemoryWindow"]] = None,
    ):
        self.__cache: MutableMapping[str, _MemoryWindow] = (
            cache if cache is not None else {}
        )
        self.__interval = interval
        self.__duration_calc = duration_func

    def get_current_window(self, hit: Hit) -> "_MemoryWindow":
        window = self.__cache.get(hit.key)
        if window is None or window.get_remaining_seconds() < 0:
            self.__cache[hit.key] = window = _MemoryWindow(
                duration=self.__duration_calc(hit.time, self.__interval)
            )
        return window


class _MemoryWindow(HitsWindow):
    __slots__ = ("__expire_at", "__hits")

    def __init__(self, duration: float):
        self.__expire_at = time.time() + duration
        self.__hits = 0
        super().__init__()

    def incr(self, hits: int = 1) -> int:
        self.__hits += hits
        return self.__hits

    def get_remaining_seconds(self) -> float:
        return self.__expire_at - time.time()


__all__ = ["MemoryStorage"]
