from typing import List, Tuple, Union

from fastapi import Depends
from starlette.middleware.base import DispatchFunction

from .base import FastAPILimiter, MiddlewareLimiter


def split_dependencies_and_middlewares(
    *limiters: Union[FastAPILimiter, MiddlewareLimiter]
) -> Tuple[List[Depends], List[DispatchFunction]]:

    dispatch_functions: List[DispatchFunction] = []
    dependencies: List[Depends] = []

    for limiter in limiters:
        if isinstance(limiter, MiddlewareLimiter):
            dispatch_functions.append(limiter.dispatch)
        elif isinstance(limiter, FastAPILimiter):
            dependencies.append(Depends(limiter))
        else:
            raise TypeError(f"Object {limiter} is not a Middleware or Limiter.")
    return dependencies, dispatch_functions
