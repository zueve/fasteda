import inspect
from collections.abc import Callable

from pydantic import BaseModel

from . import entity, interfaces


def pydantic(endpoint: Callable[..., None]) -> interfaces.Handler:
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

    def handler(event: entity.Event) -> None:
        body = param_type.parse_raw(event.body)
        endpoint(body)

    return handler
