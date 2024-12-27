from contextlib import asynccontextmanager

import pydantic

from fasteda import adapter, app


@asynccontextmanager
async def lifespan():
    print("On startup")
    try:
        yield
    finally:
        print("On shutdown")


apps = app.FastEDA(adapter=adapter.pydantic, lifespan=lifespan())


class Client(pydantic.BaseModel):
    id: int
    name: str


@apps.add("client.create.v1")
def create_client(client: Client) -> None:
    print(f"{client=} created")  # noqa: T201


@apps.add("client.update.v1")
def update_client(client: Client) -> None:
    print(f"{client=} updated")  # noqa: T201


@apps.add("client.delete.v1")
def delete_client(client: Client) -> None:
    print(f"{client=} deleted")  # noqa: T201
