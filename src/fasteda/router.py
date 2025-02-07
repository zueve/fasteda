from collections.abc import Awaitable, Callable, Mapping
from typing import TypeVar

from . import interface

T = TypeVar("T", bound=Callable[..., Awaitable[None]] | Callable[..., None])


class Router:
    def __init__(
        self,
        name: str,
        adapter: interface.HandlerAdapter,
        middlewares: list[interface.Middleware] | None = None,
    ):
        self._name = name
        self._middlewares = middlewares or []
        self._adapter = adapter
        self._routes: dict[str, Route] = {}

    def add_handler(self, topic: str, handler: interface.Handler) -> None:
        self._routes[topic] = Route(
            self._name, topic, self._middlewares, handler
        )

    def add(self, topic: str) -> Callable[[T], T]:
        def wrapper(endpoint: T) -> T:
            self.add_handler(topic, self._adapter(endpoint))
            return endpoint

        return wrapper

    def get_routes(self) -> Mapping[str, "Route"]:
        return self._routes


class Route:
    group_name: str
    topic: str
    middlewares: list[interface.Middleware]
    handler: interface.Handler

    def __init__(
        self,
        router_name: str,
        topic: str,
        middlewares: list[interface.Middleware],
        handler: interface.Handler,
    ):
        self.topic = topic
        self.router_name = router_name
        self.middlewares = middlewares
        self.handler = handler
        self._handler = self._wrap_handler(handler, middlewares)

    def add_middlewares(self, middlewares: list[interface.Middleware]) -> None:
        self.middlewares = middlewares + self.middlewares
        self._handler = self._wrap_handler(self._handler, middlewares)

    def __call__(self, event: interface.Event) -> Awaitable[None]:
        return self._handler(event)

    def _wrap_handler(
        self,
        handler: interface.Handler,
        middlewares: list[interface.Middleware],
    ) -> interface.Handler:
        for mw in reversed(middlewares):

            def wrapper(
                next_: interface.Handler, mw: interface.Middleware = mw
            ) -> interface.Handler:
                async def wrapped(event: interface.Event) -> None:
                    return await mw(event, next_)

                return wrapped

            handler = wrapper(handler, mw)
        return handler
