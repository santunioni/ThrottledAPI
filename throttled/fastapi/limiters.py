from abc import ABC
from typing import Callable, List, Sequence

from fastapi import Depends
from starlette.requests import Request

from throttled import Hit
from throttled.strategy import Strategy


class Limiter(ABC):
    def __init__(self, strategy: Strategy):
        self._strategy = strategy


class GlobalLimiter(Limiter):
    def __call__(self):
        hit = Hit()
        self._strategy(hit)


class HostBasedLimiter(Limiter):
    def __call__(self, request: Request):
        hit = Hit(key=request.client.host)
        self._strategy(hit)


def as_dependencies(limiters: Sequence[Callable]) -> List[Depends]:
    return [Depends(limiter) for limiter in limiters]
