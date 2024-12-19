# FastEDA

*Like FastAPI but for event processing*

Current status: **WIP**

## Example of usage

```python
import pydantic
from fasteda import adapter, app


apps = app.FastEDA(adder=adapter.pydantic, middlewares=[])

class Client(pydantic.BaseModel):
    id: int
    name: str

@apps.add("client.create.v1")
def create_client(client: Client) -> None:
    print(f"Client {client.id} created")  # noqa: T201

```


See more examples:

 - Parse jwt [here](examples/jwt.py)
 - Parse databus [here](examples/databus.py)
 - DLQ [here](examples/dlq.py)
