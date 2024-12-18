import inspect
from collections.abc import Awaitable, Callable

from pydantic import BaseModel

from . import interfaces


def pydantic(
    endpoint: Callable[..., Awaitable[None]] | Callable[..., None],
) -> interfaces.Handler:
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

    async def handler(event: interfaces.Event) -> None:
        body = param_type.parse_raw(event.body)
        if inspect.iscoroutinefunction(endpoint):
            await endpoint(body)
        else:
            endpoint(body)
        return None

    return handler
