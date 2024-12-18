import json
from collections.abc import Awaitable, Callable, Mapping
from typing import Protocol


class Event(Protocol):
    topic: str
    headers: Mapping[str, str]
    body: bytes


Handler = Callable[[Event], Awaitable[None]]


class DatabusExtractHeaders:
    async def __call__(self, event: Event, next_: Handler) -> None:
        databus_headers = json.loads(event.body)
        body = str(databus_headers.pop("body", ""))
        headers = {**event.headers, **databus_headers}
        event.body = body.encode()
        event.headers = headers
        return await next_(event)


class DatabusExtractVersion:
    def __init__(self, version: str):
        self.version = version

    async def __call__(self, event: Event, next_: Handler) -> None:
        data = json.loads(event.body)

        if self.version not in data:
            raise ValueError(f"Version {self.version} not found in data")

        payload = data[self.version]
        event.body = json.dumps(payload).encode()

        return await next_(event)
