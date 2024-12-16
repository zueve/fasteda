from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    topic: str
    headers: Mapping[str, Any]
    body: bytes
