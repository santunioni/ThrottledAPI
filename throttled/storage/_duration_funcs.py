from typing import Callable, Mapping, Type

from throttled.strategy import FixedWindowStrategy, MovingWindowStrategy
from throttled.strategy.base import Strategy

DurationCalcType = Callable[[float, float], float]


def fixed_window_duration_calc(hit_time: float, interval: float) -> float:
    return interval - hit_time % interval


def moving_window_duration_calc(_: float, interval: float) -> float:
    return interval


DURATION_FUNCTIONS: Mapping[Type[Strategy], DurationCalcType] = {
    FixedWindowStrategy: fixed_window_duration_calc,
    MovingWindowStrategy: moving_window_duration_calc,
}
