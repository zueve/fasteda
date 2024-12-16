import json

from fasteda import entity, interfaces


class DatabusExtractHeaders:
    def __call__(self, event: entity.Event, next_: interfaces.Handler) -> None:
        databus_headers = json.loads(event.body)
        body = str(databus_headers.pop("body", ""))
        headers = {**event.headers, **databus_headers}
        event.body = body.encode()
        event.headers = headers
        return next_(event)


class DatabusExtractVersion:
    def __init__(self, version):
        self.version = version

    def __call__(self, event: entity.Event, next_: interfaces.Handler) -> None:
        data = json.loads(event.body)

        if self.version not in data:
            raise ValueError(f"Version {self.version} not found in data")

        payload = data[self.version]
        event.body = json.dumps(payload).encode()

        return next_(event)
