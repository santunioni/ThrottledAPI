import pytest
from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from throttled.fastapi import TotalLimiter
from throttled.models import Rate
from throttled.strategy import FixedWindowStrategy


@pytest.fixture
def limit() -> Rate:
    return Rate(4, 10)


@pytest.fixture
def app() -> FastAPI:
    api = FastAPI()

    @api.get("/{path}")
    def route(path: str):
        return f"Hello {path}"

    return api


def test_my_test(app, limit):
    # FIXME: because the FixedWindowStrategy depends on epoch, the test sometimes fails
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=TotalLimiter(strategy=FixedWindowStrategy(limit=limit)).dispatch,
    )
    client = TestClient(app)

    for _ in range(limit.hits):
        assert client.get("/there").json() == "Hello there"

    blocked_response = client.get("/there")
    assert blocked_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    print(blocked_response.headers["retry-after"])
    assert (
        limit.interval - 1
        <= int(blocked_response.headers["retry-after"])
        <= limit.interval
    )
