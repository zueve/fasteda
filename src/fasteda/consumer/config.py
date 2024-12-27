from typing import Any

from pydantic import BaseModel, ImportString
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import interface


class AIOKafka(BaseModel):
    bootstrap_servers: str = "kafka:9092"
    group_id: str
    group_instance_id: str | None = None
    fetch_max_wait_ms: int = 500
    fetch_max_bytes: int = 52428800
    fetch_min_bytes: int = 1
    max_partition_fetch_bytes: int = 1048576
    request_timeout_ms: int = 40000
    retry_backoff_ms: int = 100
    auto_offset_reset: str = "latest"
    # enable_auto_commit: bool = True
    # auto_commit_interval_ms: int = 1000
    check_crcs: bool = True
    metadata_max_age_ms: int = 300000
    max_poll_interval_ms: int = 300000
    rebalance_timeout_ms: int | None = None
    session_timeout_ms: int = 10000
    heartbeat_interval_ms: int = 3000
    consumer_timeout_ms: int = 200
    max_poll_records: int | None = None
    security_protocol: str = "PLAINTEXT"
    api_version: str | tuple[int, int, int] = "auto"
    exclude_internal_topics: bool = True
    connections_max_idle_ms: int = 540000
    isolation_level: str = "read_uncommitted"


class Consumer(BaseSettings):
    topics: set[str] = set()
    app: ImportString[interface.App]
    aiokafka: AIOKafka

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    @classmethod
    def from_env(cls, **kwargs: Any) -> "Consumer":
        return cls(**kwargs)
