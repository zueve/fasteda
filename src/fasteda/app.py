from collections.abc import Awaitable, Callable
from typing import TypeVar

from . import interface

T = TypeVar("T", bound=Callable[..., Awaitable[None]] | Callable[..., None])


class FastEDA:
    def __init__(
        self,
        adder: interface.HandlerAdapter,
        middlewares: list[interface.Middleware] | None = None,
    ):
        self._handlers: dict[str, interface.Handler] = {}
        self._adder = adder
        self._middlewares = middlewares or []

    def add_handler(self, topic: str, handler: interface.Handler) -> None:
        for mw in reversed(self._middlewares):

            def wrapper(next_: interface.Handler, mw=mw) -> interface.Handler:
                async def wrapped(event: interface.Event) -> None:
                    return await mw(event, next_)

                return wrapped

            handler = wrapper(handler, mw)
        self._handlers[topic] = handler

    def add(self, topic: str) -> Callable[[T], T]:
        def wrapper(endpoint: T) -> T:
            self.add_handler(topic, self._adder(endpoint))
            return endpoint

        return wrapper

    async def handle(self, event: interface.Event):
        handler = self._handlers.get(event.topic, None)
        if not handler:
            raise ValueError(f"No handler for topic {event.topic}")
        return await handler(event)
