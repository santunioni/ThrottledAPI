from math import tanh
from pkgutil import ModuleInfo, walk_packages
from types import ModuleType
from typing import Iterable, Optional, Sequence


def get_packages_in_module(module: ModuleType) -> Iterable[ModuleInfo]:
    return walk_packages(module.__path__, prefix=module.__name__ + ".")


def get_package_paths_in_module(module: ModuleType) -> Sequence[str]:
    return [package.name for package in get_packages_in_module(module)]


class NumbersComparer:
    """
    A simple class for comparing numbers, given an error
    """

    __slots__ = ("__error",)

    def __init__(self, error: float = 1e-2, interval: Optional[float] = None):
        self.__error = error
        if interval is not None:
            self.__error = interval * (0.15 - 0.10 * tanh(interval))

    def almost_equals(self, retry_after: float, interval: float) -> bool:
        """Checks if two numbers are almost equal, given an error."""
        return abs(retry_after - interval) <= self.__error


NOT_SET = object()


class Context:
    """
    A simple class for storing a test context.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return NOT_SET
