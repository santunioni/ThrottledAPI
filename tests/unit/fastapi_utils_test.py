import random
import time

import pytest
from fastapi import Depends
from starlette.requests import Request

from throttled.fastapi import (
    FastAPILimiter,
    IPLimiter,
    TotalLimiter,
    split_dependencies_and_middlewares,
)
from throttled.strategies import Strategies


class DependencyLimiter(FastAPILimiter):
    def __call__(self, request: Request, current_time=Depends(time.time)):
        self.limit(str(current_time))


def test_should_split_dependencies_and_middlewares(limit, storage):
    # Given all 3 limiters are defined
    dependency_limiter = DependencyLimiter(
        limit=limit, storage=storage, strategy=Strategies.MOVING_WINDOW
    )
    ip_limiter = IPLimiter(
        limit=limit, storage=storage, strategy=Strategies.MOVING_WINDOW
    )
    total_limiter = TotalLimiter(
        limit=limit, storage=storage, strategy=Strategies.MOVING_WINDOW
    )

    # And their order is random
    limiters = [dependency_limiter, total_limiter, ip_limiter]
    random.shuffle(limiters)

    # When spliting dependencies and middlewares
    dependencies, dispatch_functions = split_dependencies_and_middlewares(*limiters)

    # Should have only 1 dependency
    assert len(dependencies) == 1
    assert dependencies.pop().dependency is dependency_limiter
    
    # And dispatch functions should contain the other 2 limiters
    assert ip_limiter.dispatch in dispatch_functions
    assert total_limiter.dispatch in dispatch_functions


def test_should_raise_if_not_callable_limiter():
    obj = object()
    with pytest.raises(TypeError) as err:
        _ = split_dependencies_and_middlewares(obj)

    assert err.value.args[0] == f"Object {obj} is not a Middleware or Limiter."
