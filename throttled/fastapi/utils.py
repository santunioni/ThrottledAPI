from typing import Callable, List, Tuple, Union

from fastapi import Depends
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction

from throttled.limiter import Limiter

from .base import Middleware, catcher_middleware


def split_dependencies_and_middlewares(
    *limiters: Union[Limiter, Middleware], include_catcher: bool = True
) -> Tuple[List[Depends], List[Callable[[Starlette], BaseHTTPMiddleware]]]:

    dispatch_functions: List[DispatchFunction] = []
    if include_catcher:
        dispatch_functions.append(catcher_middleware)

    dependencies: List[Depends] = []
    for limiter in limiters:
        if isinstance(limiter, Middleware):
            dispatch_functions.append(limiter.dispatch)
        elif isinstance(limiter, Limiter):
            if callable(limiter):
                dependencies.append(Depends(limiter))
            else:
                raise TypeError(f"Object {limiter} is not Callable.")
        else:
            raise TypeError(f"Object {limiter} is not a Middleware or Limiter.")
    return dependencies, [
        lambda app: BaseHTTPMiddleware(app, dispatch=df) for df in dispatch_functions
    ]
