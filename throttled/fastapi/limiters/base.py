from abc import ABC

from throttled.strategy import Strategy


class Limiter(ABC):
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def __call__(self, *args, **kwargs):
        ...
