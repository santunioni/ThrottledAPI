import pytest
from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from throttled.fastapi import IPLimiter, MiddlewareLimiter, TotalLimiter
from throttled.fastapi.base import null_detail_factory
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
def middleware_limiter(request, limit) -> MiddlewareLimiter:
    return request.param(
        limit=limit,
        storage=MemoryStorage(),
        strategy=Strategies.MOVING_WINDOW,
    )


def test_middleware_should_limit_next_request(app, limit, middleware_limiter, comparer):
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


def test_middleware_should_ignore_ignored_path(app, limit, comparer):
    limiter = IPLimiter(
        limit=limit,
        storage=MemoryStorage(),
        strategy=Strategies.MOVING_WINDOW,
        detail_factory=null_detail_factory,
    )
    limiter.ignore_path("/there")
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=limiter.dispatch,
    )
    client = TestClient(app)

    for _ in range(2 * limit.hits):
        assert client.get("/there").json() == "Hello there"

    for _ in range(limit.hits):
        assert client.get("/vini").content == b'"Hello vini"'
    for _ in range(limit.hits):
        assert client.get("/vini").content == b""
