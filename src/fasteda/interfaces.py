from collections.abc import Callable, Mapping
from typing import Protocol


class Event(Protocol):
    topic: str
    headers: Mapping[str, str]
    body: bytes


Handler = Callable[[Event], None]

HandlerAdder = Callable[[Callable[..., None]], Handler]

Middleware = Callable[[Event, Handler], None]
