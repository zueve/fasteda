from collections.abc import Mapping
from dataclasses import dataclass


@dataclass
class Event:
    topic: str
    headers: Mapping[str, str]
    value: bytes
