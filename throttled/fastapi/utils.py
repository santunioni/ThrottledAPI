from typing import List, Tuple, Type, Union

from fastapi import Depends
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction

from throttled.limiter import Limiter

from .base import Middleware, catcher_middleware


def _create_middleware(dispatch: DispatchFunction) -> Type[BaseHTTPMiddleware]:
    return type("MyLimiterMiddleware", (BaseHTTPMiddleware,), {"dispatch": dispatch})  # type: ignore


def split_dependencies_and_middlewares(
    *limiters: Union[Limiter, Middleware], include_catcher: bool = True
) -> Tuple[List[Depends], List[Type]]:

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
    return dependencies, list(map(_create_middleware, dispatch_functions))
