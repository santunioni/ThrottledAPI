from pytest_bdd import scenario

from ..utils_for_test import get_package_paths_in_module
from . import steps

pytest_plugins = get_package_paths_in_module(steps)


@scenario("features/fastapi_limiter.feature", "The limiter is ignoring a given path")
def test_fastapi_limiter_should_ignore_ignored_paths():
    pass


@scenario("features/fastapi_limiter.feature", "There is a global limiter in the API")
def test_fastapi_limiter_should_limiter_excessive_requests():
    pass
