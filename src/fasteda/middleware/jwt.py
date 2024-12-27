import base64

from jwcrypto import jwk, jwt

from fasteda import interface


class JWTValidate:
    def __init__(self, key: jwk.JWK):
        self.key = key

    async def __call__(
        self, event: interface.Event, next_: interface.Handler
    ) -> None:
        jwt.JWT(key=self.key, jwt=event.value.decode())
        return await next_(event)


class JWTExtractPayload:
    async def __call__(
        self, event: interface.Event, next_: interface.Handler
    ) -> None:
        token = event.value.decode()
        _, payload, _ = token.split(".")
        payload += "=" * ((4 - len(payload) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload)
        event.value = decoded_payload
        return await next_(event)
