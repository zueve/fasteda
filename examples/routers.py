import asyncio

import pydantic

from fasteda import adapter, app, entity, interface, router


class PrintMideleware:
    def __init__(self, message: str):
        self.message = message

    async def __call__(
        self, event: interface.Event, next_: interface.Handler
    ) -> None:
        print(self.message)
        return await next_(event)


group1 = router.Router(
    name="Group 1",
    adapter=adapter.pydantic,
    middlewares=[PrintMideleware("Group 1: Step 2")],
)

group2 = router.Router(
    name="Group 2",
    adapter=adapter.pydantic,
    middlewares=[PrintMideleware("Group 2: Step 2")],
)


class Client(pydantic.BaseModel):
    id: int
    name: str


@group1.add("client.create.v1")
def create_client(client: Client) -> None:
    print("Step 3")  # noqa: T201


@group2.add("client.update.v1")
def update_client(client: Client) -> None:
    print("Step 3")  # noqa: T201


apps = app.FastEDA(
    adapter=adapter.pydantic,
    middlewares=[PrintMideleware("Step 1")],
    routers=[group1, group2],
)

if __name__ == "__main__":
    event = entity.Event(
        topic="client.create.v1",
        headers={},
        value=b'{"id": 1, "name": "John Doe"}',
    )
    asyncio.run(apps.handle(event))

    event = entity.Event(
        topic="client.update.v1",
        headers={},
        value=b'{"id": 1, "name": "John Doe"}',
    )
    asyncio.run(apps.handle(event))
