import asyncio
from unittest.mock import Mock

import pydantic

from fasteda import adder, app, entity, interfaces

producer = Mock()


async def dlq_middleware(
    event: interfaces.Event, next_: interfaces.Handler
) -> None:
    try:
        return await next_(event)
    except Exception:
        event.headers = {"dlq.topic-orig": event.topic, **event.headers}
        event.topic = "dlq.topic"
        producer.send(event)


apps = app.FastEDA(
    adder=adder.pydantic,
    middlewares=[dlq_middleware],
)


class Client(pydantic.BaseModel):
    id: int
    name: str


@apps.add("client.create.v1")
def create_client(client: Client) -> None:
    raise ValueError("Something went wrong")


async def dlq(event: interfaces.Event) -> None:
    topic_orig = event.headers["dlq.topic-orig"]
    event.topic = topic_orig
    await apps.handle(event)


if __name__ == "__main__":
    apps.add_handler("dlq.topic", dlq)
    event = entity.Event(
        topic="client.create.v1",
        headers={},
        body=b'{"id": 1, "name": "John Doe"}',
    )
    asyncio.run(apps.handle(event))

    event = entity.Event(
        topic="dlq.topic",
        headers={"dlq.topic-orig": "client.create.v1"},
        body=b'{"id": 1, "name": "John Doe"}',
    )
    producer.send.assert_called_once_with(event)
    asyncio.run(apps.handle(event))
    producer.send.assert_called_with(event)
