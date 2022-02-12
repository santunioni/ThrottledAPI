from typing import Callable, Mapping

from throttled.strategies import Strategies

DurationCalcType = Callable[[float, float], float]


def fixed_window_duration_calc(hit_time: float, interval: float) -> float:
    return interval - hit_time % interval


def moving_window_duration_calc(_: float, interval: float) -> float:
    return interval


DUR_REGISTRY: Mapping[Strategies, DurationCalcType] = {
    Strategies.FIXED_WINDOW: fixed_window_duration_calc,
    Strategies.MOVING_WINDOW: moving_window_duration_calc,
}
