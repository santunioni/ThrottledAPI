import time

from throttled.storage.base import HitsWindow


class MemoryWindow(HitsWindow):
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
