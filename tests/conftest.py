import fakeredis
import pytest

from tests.utils_for_test import Context, NumbersComparer
from throttled.limiter import Limiter
from throttled.models import Rate
from throttled.storage import BaseStorage
from throttled.storage.memory import MemoryStorage
from throttled.storage.redis import RedisStorage
from throttled.strategies import Strategies


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
    This comparer implements error tolerance for comparing numbers in steps.
    Tolerance: from 5% for larger intervals to 15% for smaller intervals.

    :return: Error tolerance when comparing numbers
    """
    return NumbersComparer(interval=limit.interval)
