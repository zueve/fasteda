from collections.abc import Awaitable, Callable
from typing import TypeVar

from . import interfaces

T = TypeVar("T", bound=Callable[..., Awaitable[None]] | Callable[..., None])


class FastEDA:
    def __init__(
        self,
        adder: interfaces.HandlerAdder,
        middlewares: list[interfaces.Middleware] | None = None,
    ):
        self._handlers: dict[str, interfaces.Handler] = {}
        self._adder = adder
        self._middlewares = middlewares or []

    def add_handler(self, topic: str, handler: interfaces.Handler) -> None:
        for mw in reversed(self._middlewares):

            def wrapper(
                next_: interfaces.Handler, mw=mw
            ) -> interfaces.Handler:
                async def wrapped(event: interfaces.Event) -> None:
                    return await mw(event, next_)

                return wrapped

            handler = wrapper(handler, mw)
        self._handlers[topic] = handler

    def add(self, topic: str) -> Callable[[T], T]:
        def wrapper(endpoint: T) -> T:
            self.add_handler(topic, self._adder(endpoint))
            return endpoint

        return wrapper

    async def handle(self, event: interfaces.Event):
        handler = self._handlers.get(event.topic, None)
        if not handler:
            raise ValueError(f"No handler for topic {event.topic}")
        return await handler(event)
