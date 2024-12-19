from collections.abc import Awaitable, Callable, Mapping
from typing import Protocol


class Event(Protocol):
    topic: str
    headers: Mapping[str, str]
    body: bytes


Result = Awaitable[None]

Handler = Callable[[Event], Result]

HandlerAdapter = Callable[
    [Callable[..., Result] | Callable[..., None]], Handler
]

Middleware = Callable[[Event, Handler], Result]
