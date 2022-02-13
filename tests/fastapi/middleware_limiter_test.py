from typing import List

import pytest
from fastapi import FastAPI
from requests import Response
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from throttled.fastapi import IPLimiter, MiddlewareLimiter, TotalLimiter
from throttled.fastapi.base import key_detail_factory
from throttled.storage.memory import MemoryStorage
from throttled.strategies import Strategies


@pytest.fixture
def app() -> FastAPI:
    api = FastAPI()

    @api.get("/{path}")
    def route(path: str):
        return f"Hello {path}"

    return api


@pytest.fixture(params=[IPLimiter, TotalLimiter])
def limiter(request, limit) -> MiddlewareLimiter:
    return request.param(
        limit=limit,
        storage=MemoryStorage(),
        strategy=Strategies.MOVING_WINDOW,
        detail_factory=key_detail_factory,
    )


@pytest.fixture
def client(limit, limiter, app):
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=limiter.dispatch,
    )
    return TestClient(app)


def test_middleware_should_limit_next_request(client, limit, comparer):
    # Given a rate limited API
    # And the API limit is exhausted
    for _ in range(limit.hits):
        assert client.get("/there").json() == "Hello there"

    # When I hit the API again
    response = client.get("/there")

    # The request is blocked by the limiter
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert comparer.almost_equals(
        retry_after=float(response.headers["retry-after"]),
        interval=limit.interval,
    )


def test_middleware_should_ignore_ignored_path(client, limit, limiter):
    # Given a rate limited API
    # And the rate limiter ignores a given path
    limiter.ignore_path("/there")

    # When I hit the path a number of times greater than limit
    responses: List[Response] = []
    for _ in range(2 * limit.hits):
        responses.append(client.get("/there"))

    # Then all requests are answered successfully
    assert all(r.json() == "Hello there" for r in responses)
    assert all(r.status_code == status.HTTP_200_OK for r in responses)
