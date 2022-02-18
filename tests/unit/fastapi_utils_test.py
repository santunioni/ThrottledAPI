import itertools
import time
from typing import List, Sequence

import pytest
from fastapi import Depends
from starlette.requests import Request

from throttled.fastapi import (
    FastAPILimiter,
    IPLimiter,
    TotalLimiter,
    split_dependencies_and_middlewares,
)
from throttled.models import Rate
from throttled.storage import BaseStorage
from throttled.strategies import Strategies


class DependencyLimiter(FastAPILimiter):
    def __call__(self, request: Request, current_time=Depends(time.time)):
        self.limit(str(current_time))


def given_all_limiters(limit: Rate, storage: BaseStorage) -> List[FastAPILimiter]:
    return [
        DependencyLimiter(
            limit=limit, storage=storage, strategy=Strategies.MOVING_WINDOW
        ),
        IPLimiter(limit=limit, storage=storage, strategy=Strategies.MOVING_WINDOW),
        TotalLimiter(limit=limit, storage=storage, strategy=Strategies.MOVING_WINDOW),
    ]


def fastapi_dependencies_are_the_same(
    dependencies_1: Sequence[Depends], dependencies_2: Sequence[Depends]
) -> bool:
    for dep_1, dep_2 in itertools.zip_longest(dependencies_1, dependencies_2):
        if dep_1.dependency is not dep_2.dependency:
            return False
    return True


def test_should_split_dependencies_and_middlewares(limit, storage):
    # Given 2 middleware limiters and 1 limiter as dependency
    limiters = given_all_limiters(limit, storage)
    dependency_limiiter, ip_limiter, total_limiter = limiters

    # When spliting dependencies and middlewares
    dependencies, dispatch_functions = split_dependencies_and_middlewares(*limiters)

    # Then it should return only limiter as dependency
    assert fastapi_dependencies_are_the_same(dependencies, [Depends(dependency_limiiter)])

    # And the other two limiters dispatch method as dispatch functions
    assert dispatch_functions == [ip_limiter.dispatch, total_limiter.dispatch]


def test_should_raise_if_not_callable_limiter():
    obj = object()
    with pytest.raises(TypeError) as err:
        _ = split_dependencies_and_middlewares(obj)

    assert err.value.args[0] == f"Object {obj} is not a Middleware or Limiter."
