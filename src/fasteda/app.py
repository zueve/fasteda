from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import TypeVar

from . import interface, router

T = TypeVar("T", bound=Callable[..., Awaitable[None]] | Callable[..., None])


@asynccontextmanager
async def empty():
    yield


class FastEDA(router.Router):
    def __init__(
        self,
        adapter: interface.HandlerAdapter,
        middlewares: list[interface.Middleware] | None = None,
        routers: list[router.Router] | None = None,
        lifespan: AbstractAsyncContextManager[None] | None = None,
    ):
        self._name = "App"
        self._middlewares = middlewares or []
        self._adapter = adapter
        self._routes: dict[str, router.Route] = {}
        self._lifespan = lifespan or empty()

        for router_ in routers or []:
            for topic, route in router_.get_routes().items():
                route.add_middlewares(self._middlewares)
                self._routes[topic] = route

    async def handle(self, event: interface.Event):
        handler = self._routes.get(event.topic, None)
        if not handler:
            raise ValueError(f"No handler for topic {event.topic}")
        return await handler(event)

    def get_topics(self) -> set[str]:
        return set(self._routes.keys())

    async def __aenter__(self):
        await self._lifespan.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._lifespan.__aexit__(exc_type, exc_val, exc_tb)
