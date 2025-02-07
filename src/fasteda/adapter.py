import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel

from fasteda import dependency

from . import interface


def pydantic(
    endpoint: Callable[..., Awaitable[None]] | Callable[..., None],
) -> interface.Handler:
    # extract type of T from signature of endpoint
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


class DI:
    def __init__(self, injector: dependency.Injector | None = None) -> None:
        self._injector = injector or dependency.Injector()

        self._injector.add_provider(headers_provider)
        self._injector.add_provider(header_provider)
        self._injector.add_provider_resolver(base_model_resolver)

    def __call__(
        self, endpoint: Callable[..., Awaitable[None]] | Callable[..., None]
    ) -> interface.Handler:
        sign = dict(inspect.signature(endpoint).parameters)

        for param in sign.values():
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                raise ValueError(
                    "Endpoint parameter must have type annotation"
                )

        async def handler(event: interface.Event) -> None:
            def event_provider() -> interface.Event:
                return event

            self._injector.bind_provider(interface.Event, event_provider)
            result = self._injector.run(endpoint)
            if inspect.isawaitable(result):
                await result
            return

        return handler


def headers_provider(event: interface.Event) -> interface.Headers:
    return event.headers


def header_provider(
    param: inspect.Parameter, headers: interface.Headers
) -> interface.Header:
    if param.name not in headers:
        raise ValueError(f"Header {param.name} not found")
    return headers[param.name]


def base_model_resolver(
    cls: type[Any],
) -> dependency.Provider[Any] | None:
    if issubclass(cls, BaseModel):

        def model_provider(event: interface.Event) -> Any:
            return cls.parse_raw(event.value)

        return model_provider
    return None
