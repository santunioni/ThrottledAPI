import asyncio

import pytest

from tests.utils_test import NumbersComparer
from throttled.exceptions import RateLimitExceeded
from throttled.strategies import Strategies

numbers_almost_equals = NumbersComparer(error=1e-2).almost_equals


def function() -> bool:
    """Boilerplate function to test the limiter decorator."""
    return True


async def coroutine_function() -> bool:
    """Boilerplate coroutine function to test the limiter decorator."""
    return True


def test_limited_function(limit, limiter_for):
    limiter = limiter_for(Strategies.MOVING_WINDOW)
    limited_func = limiter.decorate(function)

    ret = [limited_func() for _ in range(limit.hits)]

    with pytest.raises(RateLimitExceeded) as err:
        limited_func()

    assert all(ret)
    assert numbers_almost_equals(err.value.retry_after, limit.interval)


async def test_limited_coroutine_function(limit, limiter_for):
    limiter = limiter_for(Strategies.MOVING_WINDOW)
    limited_coroutine_func = limiter.decorate(coroutine_function)

    ret = await asyncio.gather(*(limited_coroutine_func() for _ in range(limit.hits)))

    with pytest.raises(RateLimitExceeded) as err:
        await limited_coroutine_func()

    assert all(ret)
    assert numbers_almost_equals(err.value.retry_after, limit.interval)
