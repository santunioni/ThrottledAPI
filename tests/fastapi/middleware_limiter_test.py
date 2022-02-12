from math import tanh

import pytest
from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from tests.utils_test import NumbersComparer
from throttled.fastapi import IPLimiter, MiddlewareLimiter, TotalLimiter
from throttled.storage.memory import MemoryStorage
from throttled.strategies import Strategies


@pytest.fixture
def comparer(limit) -> NumbersComparer:
    """
    Error tolerance
    From 5% for larger intervals to 15% for smaller intervals.

    :return: Error tolerance when comparing numbers
    """
    return NumbersComparer(error=limit.interval * (0.15 - 0.10 * tanh(limit.interval)))


@pytest.fixture
def app() -> FastAPI:
    api = FastAPI()

    @api.get("/{path}")
    def route(path: str):
        return f"Hello {path}"

    return api


@pytest.fixture(params=[IPLimiter, TotalLimiter])
def middleware_limiter(request, limit) -> MiddlewareLimiter:
    return request.param(
        limit=limit, storage=MemoryStorage(), strategy=Strategies.MOVING_WINDOW
    )


def test_middleware_limiter(app, limit, middleware_limiter, comparer):
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=middleware_limiter.dispatch,
    )
    client = TestClient(app)

    for _ in range(limit.hits):
        assert client.get("/there").json() == "Hello there"

    blocked_response = client.get("/there")

    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert comparer.almost_equals(
        retry_after=float(blocked_response.headers["retry-after"]),
        interval=limit.interval,
    )
