from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import TypeVar

from . import interface

T = TypeVar("T", bound=Callable[..., Awaitable[None]] | Callable[..., None])


@asynccontextmanager
async def empty():
    yield


class FastEDA:
    def __init__(
        self,
        adapter: interface.HandlerAdapter,
        middlewares: list[interface.Middleware] | None = None,
        groups: list["Group"] | None = None,
        lifespan: AbstractAsyncContextManager[None] | None = None,
    ):
        self._handlers: dict[str, interface.Handler] = {}
        self._adapter = adapter
        self._middlewares = middlewares or []
        self._lifespan = lifespan or empty()

        for group in groups or []:
            for topic, handler in group.handlers.items():
                handler = self._wrap_handler(handler, group.middlewares)
                self.add_handler(topic, handler)

    def add_handler(self, topic: str, handler: interface.Handler) -> None:
        self._handlers[topic] = self._wrap_handler(handler, self._middlewares)

    def add(self, topic: str) -> Callable[[T], T]:
        def wrapper(endpoint: T) -> T:
            self.add_handler(topic, self._adapter(endpoint))
            return endpoint

        return wrapper

    async def handle(self, event: interface.Event):
        handler = self._handlers.get(event.topic, None)
        if not handler:
            raise ValueError(f"No handler for topic {event.topic}")
        return await handler(event)

    def get_topics(self) -> set[str]:
        return set(self._handlers.keys())

    def _wrap_handler(
        self,
        handler: interface.Handler,
        middlewares: list[interface.Middleware],
    ) -> interface.Handler:
        for mw in reversed(middlewares):

            def wrapper(next_: interface.Handler, mw=mw) -> interface.Handler:
                async def wrapped(event: interface.Event) -> None:
                    return await mw(event, next_)

                return wrapped

            handler = wrapper(handler, mw)
        return handler

    async def __aenter__(self):
        await self._lifespan.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._lifespan.__aexit__(exc_type, exc_val, exc_tb)


class Group:
    def __init__(
        self,
        name: str,
        adapter: interface.HandlerAdapter,
        middlewares: list[interface.Middleware] | None = None,
    ):
        self.name = name
        self.middlewares = middlewares or []
        self.adapter = adapter
        self.handlers: dict[str, interface.Handler] = {}

    def add_handler(self, topic: str, handler: interface.Handler) -> None:
        self.handlers[topic] = handler

    def add(self, topic: str) -> Callable[[T], T]:
        def wrapper(endpoint: T) -> T:
            self.add_handler(topic, self.adapter(endpoint))
            return endpoint

        return wrapper
