from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

import aiokafka

type ConsumerRecordType = aiokafka.ConsumerRecord[bytes, bytes]
type Handler = Callable[[ConsumerRecordType], Awaitable[None]]


class Event(Protocol):
    topic: str
    headers: Mapping[str, str]
    value: bytes


@runtime_checkable
class App(AbstractAsyncContextManager["App"], Protocol):
    def get_topics(self) -> set[str]: ...
    async def handle(self, event: Event) -> None: ...
