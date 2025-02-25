fmt:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check
	uv run ruff format --check .
	uv run mypy .

test:
	uv run examples/jwt.py
	uv run examples/databus.py
	uv run examples/dlq.py
	uv run examples/dlq_v2.py
	uv run examples/lifespan.py
	uv run examples/routers.py
