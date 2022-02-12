import pytest
import redislite

from throttled.limiter import Limiter
from throttled.models import Rate
from throttled.storage import BaseStorage
from throttled.storage.memory import MemoryStorage
from throttled.storage.redis import RedisStorage
from throttled.strategies import Strategies


def redis() -> RedisStorage:
    return RedisStorage(client=redislite.Redis())


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
