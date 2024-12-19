import asyncio

import pydantic
from jwcrypto import jwk

from fasteda import adapter, app, entity, middleware

private_key = jwk.JWK.from_json(
    '{"d":"iFdVmc0DSxB1A9Mff3whz1wyMmb70WIIRykNOhNwPH-I_7RhhnoeVidm3wq78ERJsQ8Swrd4gNo9x65XY7kJPxFPEPEnGovB2Pysbxy0PQLMRiO9k9BhBkXzMqDcaL6wORbtZwvyPsdZnnk5gDb_xjChiiGtg8qLnpG_HcHKkIk","dp":"BCQlKiZpu6eo7o4t2ivVH2itVCELqgDy6rg75k9cp8Aw4Mpb-mRIsMp5iI-hSMl_PMToaEzP0c4eEB_EeF_QaQ","dq":"qIaI0QBn2sL9VL_9dhGFYkrq-EvSAYqg3yi58-iubvI3sEAkVAKEH3ACeDVlcTnFrTENeXPg1RavnOJLjLygaQ","e":"AQAB","kty":"RSA","n":"snGWdvgu_m8vhDKxAXsQGgB6ciLRGbRda6TbhgASu0xGYlRSDxcPrRXQnCmRsGPtawcQgHoFAwfGLZAIb5Nv9Ym_FlyFvMPqQkAzPV6Gv7jTozbjTcofqZKsxYvDoxi97xrXa_BInrvEoEZkZ_R0nLK1bEwDFKjd67n8lspM2QE","p":"4WqXBrbVEHSkngDv6j7JaCS6bjgWwuT605fyFRr-9flUaHL7DoOh0r8Bfvi85jnWzrO0j_5TDgUTMARg_KiQww","q":"yqd9ykTsCsxZeNHFS0hfZA2D5SBFgcJ_BaAbMM6wnWEwZKutf42TXwkL5PsVxRySqXiBnkQaHwmCsbcZyvDS6w","qi":"WF0vbLEe-1jTh9IaBCaX1pvE-Y4APe0ELIPxpls9wlymlKfchvgI43d3oKyxhCSE8CQkJ8pmDjPZe6BnOrqnBQ"}'
)
public_key = jwk.JWK.from_json(private_key.export_public())

apps = app.FastEDA(
    adder=adapter.pydantic,
    middlewares=[
        middleware.DatabusExtractHeaders(),
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
    print(f"Client {client} created")  # noqa: T201


if __name__ == "__main__":
    data = """{
        "id": "1234",
        "created_at": 1568732261.4411473,
        "producer": "payment-platform",
        "body": "eyJhbGciOiJSUzI1NiJ9.eyIxLjAuMCI6eyJpZCI6MSwibmFtZSI6IkpvaG4gRG9lIn19.qWjCO_RLb4zAzVvZn9uNvhSuaIGmSQTXaVZH7ZQaqQnAdEMejRebPzACNNn5SmScKU4w5S9mUTOrcXyFPLm02rFFgCw5FSSl84lgjrHowT5I6EUp_PoGAzJTiuCwPh0IPoUay-XznoPeKFmudVCHPskI2Aitx7OFeJ2hjqXTSuE"
    }"""  # noqa: E501
    event = entity.Event(
        topic="client.create.v1",
        headers={},
        body=data.encode(),
    )
    asyncio.run(apps.handle(event))
