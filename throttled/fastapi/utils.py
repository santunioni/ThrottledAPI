from typing import List, Tuple, Union

from fastapi import Depends
from starlette.middleware.base import DispatchFunction

from .base import FastAPILimiter, FastAPIRequestLimiter


def split_dependencies_and_middlewares(
    *limiters: Union[FastAPILimiter, FastAPIRequestLimiter]
) -> Tuple[List[Depends], List[DispatchFunction]]:
    dispatch_functions: List[DispatchFunction] = []

    dependencies: List[Depends] = []
    for limiter in limiters:
        if isinstance(limiter, FastAPIRequestLimiter):
            dispatch_functions.append(limiter.dispatch)
        elif isinstance(limiter, FastAPILimiter):
            if callable(limiter):
                dependencies.append(Depends(limiter))
            else:
                raise TypeError(f"Object {limiter} is not Callable.")
        else:
            raise TypeError(f"Object {limiter} is not a Middleware or Limiter.")
    return dependencies, dispatch_functions
