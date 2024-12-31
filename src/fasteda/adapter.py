import inspect
from collections.abc import Awaitable, Callable

from pydantic import BaseModel

from . import interface


def pydantic(
    endpoint: Callable[..., Awaitable[None]] | Callable[..., None],
) -> interface.Handler:
    # extratc type of T from signature of endpoint
    sign = dict(inspect.signature(endpoint).parameters)
    if len(sign) != 1:
        raise ValueError("Endpoint must have exactly one parameter")
    param = sign.popitem()[1]
    param_type = param.annotation

    if param_type == inspect.Parameter.empty:
        raise ValueError("Endpoint parameter must have type annotation")

    if not issubclass(param_type, BaseModel):
        raise ValueError("Endpoint parameter must be subclass of BaseModel")

    async def handler(event: interface.Event) -> None:
        value = param_type.parse_raw(event.value)
        if inspect.iscoroutinefunction(endpoint):
            await endpoint(value)
        else:
            endpoint(value)
        return

    return handler
