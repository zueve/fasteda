import random
from contextlib import asynccontextmanager
from functools import lru_cache

import aiokafka
import pydantic

from fasteda import adapter, app, interface
from fasteda.middleware.dlq import DLQ, HEADER_TOPIC_ORIG

DLQ_TOPIC = "myapp.dlq"


@lru_cache
def get_producer() -> aiokafka.AIOKafkaProducer:
    # Need wrapper becouse AIOKafkaProducer should be created with running loop
    return aiokafka.AIOKafkaProducer(
        bootstrap_servers="kafka:9092",
    )


@asynccontextmanager
async def lifespan():
    async with get_producer():
        yield


apps = app.FastEDA(
    adapter=adapter.pydantic,
    middlewares=[DLQ(DLQ_TOPIC, get_producer)],
    lifespan=lifespan(),
)


async def dlq(event: interface.Event) -> None:
    topic_orig = event.headers[HEADER_TOPIC_ORIG]
    event.topic = topic_orig
    await apps.handle(event)


apps.add_handler(DLQ_TOPIC, dlq)


class Client(pydantic.BaseModel):
    id: int
    name: str


@apps.add("myapp.create.v1")
def create_client(client: Client) -> None:
    print(f"{client=} creating")
    if random.random() > 0.01:  # noqa: S311
        raise ValueError("Something went wrong")
    print(f"{client=} created")
