"""
Fixed window rate limiter is very hard to test because we can't control
at what time we are hitting the limited resources.

Therefore, we are only testing the retry_after parameter is lesser then
the interval for the window.
"""

import asyncio
import time

import pytest

from throttled.exceptions import RateLimitExceeded
from throttled.strategies import Strategies


def time_in_window(limit) -> float:
    return time.time() % limit.interval


@pytest.fixture
def key() -> str:
    return "my-custom-key"


def time_to_window_begin(limit):
    imprecision = limit.interval * 1e-5
    return limit.interval - time_in_window(limit) + imprecision


async def test_hit_fixed_window_at_begin(key, limit, limiter_for):
    """
    Hitting a fixed window at begin works the same way as first hiting a moving window.
    """
    limiter = limiter_for(Strategies.FIXED_WINDOW)
    await asyncio.sleep(time_to_window_begin(limit))

    for _ in range(limit.hits):
        limiter.limit(key)

    with pytest.raises(RateLimitExceeded) as err:
        limiter.limit(key)

    assert err.value.retry_after < limit.interval


def time_to_half_window(limit):
    tiw = time_in_window(limit)
    if tiw > limit.interval / 2:
        return limit.interval / 2 + tiw
    return limit.interval / 2 - tiw


async def test_hit_fixed_window_at_half(key, limit, limiter_for):
    limiter = limiter_for(Strategies.FIXED_WINDOW)
    await asyncio.sleep(time_to_half_window(limit))

    for _ in range(limit.hits):
        limiter.limit(key)

    with pytest.raises(RateLimitExceeded) as err:
        limiter.limit(key)

    assert err.value.retry_after < limit.interval


def time_to_window_almost_finishes(limit):
    imprecision = limit.interval * 1e-1
    return limit.interval - time_in_window(limit) - imprecision


async def test_burst_when_window_is_ending(key, limiter_for, limit):
    limiter = limiter_for(Strategies.FIXED_WINDOW)
    await asyncio.sleep(time_to_window_almost_finishes(limit))

    success = 0
    try:
        while success <= 3 * limit.hits:
            limiter.limit(key)
            success += 1
    except RateLimitExceeded as err:
        assert err.retry_after < limit.interval
        assert limit.hits <= success <= 2 * limit.hits
    else:
        assert success == 2 * limit.hits
