import abc
import asyncio
from dataclasses import dataclass, field
from typing import Any

import pydantic

from fasteda import adapter, app, dependency, entity, interface


# entity.py
class Client(pydantic.BaseModel):
    id: int
    name: str


@dataclass
class Producer:
    name: str


# service.py
@dataclass
class IRepository:
    @abc.abstractmethod
    def create(self, client: Client) -> None: ...


@dataclass
class Service:
    def __post_init__(self) -> None:
        print(f"Service {self=} initialized")

    repo: IRepository

    def create_client(self, client: Client, producer: Producer) -> None:
        if producer.name != "good_producer":
            raise ValueError(f"Forbidden producer {producer=} {client=}")
        self.repo.create(client)


# driver.py
@dataclass
class DB:
    _store: dict[Any, Any] = field(default_factory=dict)

    def add(self, key: int, client: Client) -> None:
        self._store[key] = client


# repository.py
@dataclass
class Repository(IRepository):
    db: DB

    def create(self, client: Client) -> None:
        self.db.add(client.id, client)


# consumer.py
def get_producer(producer_name: interface.Header) -> Producer:
    return Producer(name=producer_name)


def get_db() -> DB:
    return DB()


def get_repository(db: DB) -> Repository:
    return Repository(db)


def get_service(repo: Repository) -> Service:
    return Service(repo)


injector = dependency.Injector()
injector.add_provider(get_db, cachable=True)
injector.add_provider(get_repository, cachable=True)
injector.add_provider(get_service, cachable=True)
injector.add_provider(get_producer, cachable=True)

app_v1 = app.FastEDA(
    adapter=adapter.DI(injector),
)


@app_v1.add("create_client.v1")
def create_client(
    client: Client, service: Service, producer: Producer
) -> None:
    service.create_client(client, producer)


if __name__ == "__main__":
    event = entity.Event(
        topic="create_client.v1",
        headers={"producer_name": "good_producer"},
        value=b'{"id": "12", "name": "John Doe"}',
    )

    asyncio.run(app_v1.handle(event))
    asyncio.run(app_v1.handle(event))
    asyncio.run(app_v1.handle(event))
    asyncio.run(app_v1.handle(event))

    print(injector._cache_stack)
