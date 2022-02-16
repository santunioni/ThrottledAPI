from math import tanh
from typing import Optional

import fakeredis
import pytest

from throttled.limiter import Limiter
from throttled.models import Rate
from throttled.storage import BaseStorage
from throttled.storage.memory import MemoryStorage
from throttled.storage.redis import RedisStorage
from throttled.strategies import Strategies


class NumbersComparer:
    """
    A simple class for comparing numbers, given an error
    """

    __slots__ = ("__error",)

    def __init__(self, error: float = 1e-2, interval: Optional[float] = None):
        self.__error = error
        if interval is not None:
            self.__error = interval * (0.15 - 0.10 * tanh(interval))

    def almost_equals(self, retry_after: float, interval: float) -> bool:
        """Checks if two numbers are almost equal, given an error."""
        return abs(retry_after - interval) <= self.__error


NOT_SET = object()


class Context:
    """
    A simple class for storing a test context.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return NOT_SET


def redis() -> RedisStorage:
    return RedisStorage(client=fakeredis.FakeRedis())


@pytest.fixture(params=[MemoryStorage, redis])
def storage(request) -> BaseStorage:
    return request.param()


@pytest.fixture(params=[Rate(2, 1), Rate(1, 0.1), Rate(5, 2)])
def limit(request) -> Rate:
    return request.param


@pytest.fixture
def limiter_for(storage, limit):
    def fac(
        sttg: Strategies, lim: Rate = limit, strg: BaseStorage = storage
    ) -> Limiter:
        return Limiter(strategy=sttg, storage=strg, limit=lim)

    return fac


@pytest.fixture(params=Strategies)
def limiter(limiter_for, request):
    return limiter_for(request.param)


@pytest.fixture
def context():
    return Context()


@pytest.fixture
def comparer(limit) -> NumbersComparer:
    """
    This comparer implements error tolerance for comparing numbers in tests.
    Tolerance: from 5% for larger intervals to 15% for smaller intervals.

    :return: Error tolerance when comparing numbers
    """
    return NumbersComparer(interval=limit.interval)
