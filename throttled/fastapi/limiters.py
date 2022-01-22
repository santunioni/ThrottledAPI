from throttled import Hit
from throttled.strategies import Strategy


class SimpleLimiter:
    def __init__(self, strategy: Strategy):
        self.__strategy = strategy

    def __call__(self):
        hit = Hit()
        self.__strategy(hit)
