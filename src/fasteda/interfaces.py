from collections.abc import Callable

from . import entity

Handler = Callable[[entity.Event], None]

HandlerAdder = Callable[[Callable[..., None]], Handler]

Middleware = Callable[[entity.Event, Handler], None]
