from abc import ABC, abstractmethod
from typing import Callable, Sequence

from fastapi import Depends
from starlette.requests import Request

from throttled import Hit
from throttled.strategies import Strategy


class Limiter(ABC):
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Limit the api based on rate."""


class GlobalLimiter(Limiter):
    def __call__(self):
        hit = Hit()
        self._strategy(hit)


class HostBasedLimiter(Limiter):
    def __call__(self, request: Request):
        hit = Hit(key=request.client.host)
        self._strategy(hit)


def as_dependencies(limiters: Sequence[Callable]) -> Depends:
    return [Depends(limiter) for limiter in limiters]
