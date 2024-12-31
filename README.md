# FastEDA

*Like FastAPI but for event processing*

Current status: **WIP**

## Example of usage

```python
import pydantic
from fasteda import adapter, app


apps = app.FastEDA(adapter=adapter.pydantic, middlewares=[])

class Client(pydantic.BaseModel):
    id: int
    name: str

@apps.add("client.create.v1")
def create_client(client: Client) -> None:
    print(f"Client {client.id} created")  # noqa: T201

```

Run consumer:

```bash
> python -m fasteda.consumer --app examples.dlq_v2.apps --bootstrap_servers localhost:9092 --group_id my-app
```


See more examples:

 - Parse JWT [here](examples/jwt.py)
 - Parse databus [here](examples/databus.py)
 - DLQ Minimal [here](examples/dlq.py)
 - DLQ Full [here](examples/dlq_v2.py)
 - Lifespan [here](examples/lifespan.py)
 - Groups [here](examples/groups.py)
