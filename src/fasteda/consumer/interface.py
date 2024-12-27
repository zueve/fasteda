from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

import aiokafka

type ConsumerRecordType = aiokafka.ConsumerRecord[str, bytes]
type Handler = Callable[[ConsumerRecordType], Awaitable[None]]


class Event(Protocol):
    topic: str
    headers: Mapping[str, bytes]
    body: bytes


@runtime_checkable
class App(AbstractAsyncContextManager["App"], Protocol):
    async def handle(self, event: Event) -> None: ...
