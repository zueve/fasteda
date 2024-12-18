from collections.abc import Awaitable, Callable, Mapping
from typing import Protocol


class Event(Protocol):
    topic: str
    headers: Mapping[str, str]
    body: bytes


Result = Awaitable[None]

Handler = Callable[[Event], Awaitable[None]]

HandlerAdder = Callable[
    [Callable[..., Awaitable[None]] | Callable[..., None]], Handler
]

Middleware = Callable[[Event, Handler], Awaitable[None]]
