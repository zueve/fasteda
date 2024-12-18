import base64

from jwcrypto import jwk, jwt

from fasteda import interfaces


class JWTValidate:
    def __init__(self, key: jwk.JWK):
        self.key = key

    def __call__(
        self, event: interfaces.Event, next_: interfaces.Handler
    ) -> None:
        jwt.JWT(key=self.key, jwt=event.body.decode())
        return next_(event)


class JWTExtractPayload:
    def __call__(
        self, event: interfaces.Event, next_: interfaces.Handler
    ) -> None:
        token = event.body.decode()
        _, payload, _ = token.split(".")
        payload += "=" * ((4 - len(payload) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload)
        event.body = decoded_payload
        return next_(event)
