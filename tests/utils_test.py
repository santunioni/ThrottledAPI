class NumbersComparer:
    __slots__ = ("__error",)

    def __init__(self, error: float = 1e-2):
        self.__error = error

    def almost_equals(self, retry_after: float, interval: float) -> bool:
        """Checks if two numbers are almost equal, given an error."""
        return abs(retry_after - interval) <= self.__error
