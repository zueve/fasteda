import asyncio

import pydantic

from fasteda import adapter, app, entity, interface

apps = app.FastEDA(
    adapter=adapter.DI(),
    middlewares=[],
)


class Client(pydantic.BaseModel):
    id: int
    name: str


@apps.add("example.v1")
def example_v1(client: Client) -> None:
    print(f"Example v1 {client.id}")  # noqa: T201


@apps.add("example.v2")
def example_v2() -> None:
    print("Example v2")  # noqa: T201


@apps.add("example.v3")
def example_v3(event: interface.Event) -> None:
    print(f"Example v3 {event=}")  # noqa: T201


@apps.add("example.v4")
def example_v4(headers: interface.Headers) -> None:
    print(f"Example v4 {headers['my_name_header']} created")  # noqa: T201


@apps.add("example.v5")
def example_v5(my_name_header: interface.Header) -> None:
    print(f"Client {my_name_header} ")  # noqa: T201


@apps.add("example.v6")
def example_v6(
    client: Client,
    event: interface.Event,
    headers: interface.Headers,
    my_name_header: interface.Header,
) -> None:
    print(f"{client=}")  # noqa: T201
    print(f"{event=}")  # noqa: T201
    print(f"{headers=}")  # noqa: T201
    print(f"{my_name_header=}")  # noqa: T201


if __name__ == "__main__":
    event = entity.Event(
        topic="client.create.v1",
        headers={"my_name_header": "Header for topic"},
        value=b'{"id": 1, "name": "John Doe"}',
    )
    topics = [
        "example.v1",
        "example.v2",
        "example.v3",
        "example.v4",
        "example.v5",
        "example.v6",
    ]

    for topic in topics:
        event.topic = topic
        asyncio.run(apps.handle(event))
