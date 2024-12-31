import asyncio

import aiokafka

from fasteda import entity

from . import config, interface


class Consumer:
    def __init__(
        self,
        config: config.Consumer,
    ):
        supported_topics = config.app.get_topics()
        topics = config.topics or supported_topics
        if not topics.issubset(supported_topics):
            unsupporter_topics = topics - supported_topics
            raise ValueError(
                f"Topics {unsupporter_topics} are not supported by the app"
            )

        self._app = config.app
        self._client = aiokafka.AIOKafkaConsumer(
            *topics,
            bootstrap_servers=config.bootstrap_servers,
            group_id=config.group_id,
            enable_auto_commit=False,
            **config.aiokafka.model_dump(),
        )

    async def run(self) -> None:
        async with self._client, self._app:
            async for msg in self._client:
                await asyncio.shield(self.handle(msg))

    async def handle(self, msg: interface.ConsumerRecordType) -> None:
        if msg.value is None:
            msg.value = b""

        event = entity.Event(
            topic=msg.topic,
            headers={k: v.decode() for k, v in msg.headers},
            value=msg.value,
        )

        await self._app.handle(event)
        await self._client.commit()
