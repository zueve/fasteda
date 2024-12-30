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
> AIOKAFKA__GROUP_ID=my-consumer-group \
AIOKAFKA__BOOTSTRAP_SERVERS=localhost:9092 \
python -m fasteda.consumer --app examples.lifespan.apps
```


See more examples:

 - Parse JWT [here](examples/jwt.py)
 - Parse databus [here](examples/databus.py)
 - DLQ [here](examples/dlq.py)
 - Lifespan [here](examples/lifespan.py)
