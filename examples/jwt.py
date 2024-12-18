import asyncio

import pydantic
from jwcrypto import jwk, jwt

from fasteda import adder, app, entity, middleware

private_key = jwk.JWK.generate(kty="RSA", size=1024)
public_key = jwk.JWK.from_json(private_key.export_public())

apps = app.FastEDA(
    adder=adder.pydantic,
    middlewares=[
        middleware.JWTValidate(public_key),
        middleware.JWTExtractPayload(),
        middleware.DatabusExtractVersion("1.0.0"),
    ],
)


class Client(pydantic.BaseModel):
    id: int
    name: str


@apps.add("client.create.v1")
def create_client(client: Client) -> None:
    print(f"Client {client.id} created")  # noqa: T201


if __name__ == "__main__":
    msg = {"1.0.0": {"id": 1, "name": "John Doe"}}
    token = jwt.JWT(header={"alg": "RS256"}, claims=msg)
    token.make_signed_token(private_key)
    body = token.serialize()

    event = entity.Event(
        topic="client.create.v1",
        headers={},
        body=body.encode(),
    )
    asyncio.run(apps.handle(event))
