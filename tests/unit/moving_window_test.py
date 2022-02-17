import pytest

from tests.utils_for_test import NumbersComparer
from throttled.exceptions import RateLimitExceeded
from throttled.strategies import Strategies

numbers_almost_equals = NumbersComparer(error=1e-2).almost_equals


def test_limiter_should_block_after_reaching_request_limit(limit, limiter_for):
    limiter = limiter_for(Strategies.MOVING_WINDOW)
    key = "my-custom-key"

    for _ in range(limit.hits):
        limiter.limit(key)

    with pytest.raises(RateLimitExceeded) as err:
        limiter.limit(key)

    assert numbers_almost_equals(err.value.retry_after, limit.interval)
