"""
This module defines in-memory storage for WindowManager's
"""


import time
from typing import MutableMapping, Optional

from throttled.models import Hit, Rate
from throttled.storage import BaseStorage
from throttled.storage._abstract import _HitsWindow, _WindowManager
from throttled.storage._duration import DUR_REGISTRY, DurationCalcType
from throttled.strategies import Strategies


class _MemoryWindow(_HitsWindow):
    __slots__ = ("__expire_at", "__hits")

    def __init__(self, duration: float):
        self.__expire_at = time.time() + duration
        self.__hits = 0

    def incr(self, hits: int = 1) -> int:
        self.__hits += hits
        return self.__hits

    def get_remaining_seconds(self) -> float:
        return self.__expire_at - time.time()


class _MemoryWindowManager(_WindowManager):
    __slots__ = ("__interval", "__cache", "__duration_calc")

    def __init__(
        self,
        interval: float,
        duration_func: DurationCalcType,
        cache: Optional[MutableMapping[str, _MemoryWindow]] = None,
    ):
        self.__cache: MutableMapping[str, _MemoryWindow] = (
            cache if cache is not None else {}
        )
        self.__interval = interval
        self.__duration_calc = duration_func

    def get_current_window(self, hit: Hit) -> _MemoryWindow:
        window = self.__cache.get(hit.key)
        if window is None or window.is_expired():
            self.__cache[hit.key] = window = _MemoryWindow(
                duration=self.__duration_calc(hit.time, self.__interval)
            )
        return window


class MemoryStorage(BaseStorage):
    def __init__(
        self,
        cache: Optional[MutableMapping[str, _MemoryWindow]] = None,
    ):
        self.__cache = cache

    def get_window_manager(
        self, strategy: Strategies, limit: Rate
    ) -> _MemoryWindowManager:
        return _MemoryWindowManager(
            interval=limit.interval,
            duration_func=DUR_REGISTRY[strategy],
            cache=self.__cache,
        )


__all__ = ["MemoryStorage"]
