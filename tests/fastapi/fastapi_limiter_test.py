from functools import partial

import pytest
from fastapi import FastAPI
from pytest_bdd import given, parsers, scenario, then, when
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from tests.conftest import NOT_SET, NumbersComparer
from throttled.fastapi import IPLimiter, TotalLimiter
from throttled.fastapi.base import key_detail_factory
from throttled.models import Rate
from throttled.storage.memory import MemoryStorage
from throttled.strategies import Strategies

scenario = partial(scenario, "../features/fastapi_limiter.feature")


@pytest.fixture
def client(app):
    return TestClient(app)


@given(parsers.parse("A Rest API built with FastAPI"), target_fixture="app")
def app():
    api = FastAPI()

    @api.get("/{path}")
    def route(path: str):
        return f"Hello {path}"

    return api


@given(
    parsers.parse(
        "The API is limited {limiter_type} to {number} requests per {seconds} seconds"
    )
)
def build_limiter(app, limiter_type, number, seconds, context):
    number = int(number)
    seconds = float(seconds)
    limiter = {"by IP": IPLimiter, "globally": TotalLimiter}[limiter_type](
        strategy=Strategies.MOVING_WINDOW,
        storage=MemoryStorage(),
        limit=Rate(number, seconds),
        detail_factory=key_detail_factory,
    )

    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=limiter.dispatch,
    )

    if context.limiters is NOT_SET:
        context.limiters = []

    context.limiters.append(limiter)


@when(parsers.parse("I hit the API {number} times in a row"))
def hit_limiter(client, number, context):
    number = int(number)
    context.responses = []
    for _ in range(number):
        context.responses.append(client.get("/there"))


@then("All responses are successful")
def check_responses(context):
    assert all(r.ok for r in context.responses)


@then("The next hit is blocked by the limiter")
def blocked_request(client, context):
    response = client.get("/there")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    context.blocked = response


@then(parsers.parse("I should only retry after {seconds} seconds"))
def retry_after(context, seconds):
    seconds = float(seconds)

    retry_after_seconds = float(context.blocked.headers["retry-after"])
    assert NumbersComparer(interval=seconds).almost_equals(retry_after_seconds, seconds)


@given("The limiter ignores the path being tested")
def ignore_path(context):
    for limiter in context.limiters:
        limiter.ignore_path("/there")


@scenario("The limiter is ignoring a given path")
def test_fastapi_limiter_should_ignore_ignored_paths():
    pass


@scenario("There is a global limiter in the API")
def test_fastapi_limiter_should_limiter_excessive_requests():
    pass
