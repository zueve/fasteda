import asyncio

import aiokafka

from fasteda import entity

from . import config, interface


class Consumer:
    def __init__(
        self,
        config: config.Consumer,
    ):
        topics = config.topics
        supported_topics = config.app.get_topics()
        if not topics:
            topics = supported_topics
        elif not topics.issubset(supported_topics):
            unsupporter_topics = topics - supported_topics
            raise ValueError(
                f"Topics {unsupporter_topics} are not supported by the app"
            )

        topics = (
            config.app.get_topics() if not config.topics else config.topics
        )
        client = aiokafka.AIOKafkaConsumer(
            *topics,
            **config.aiokafka.model_dump(),
            enable_auto_commit=False,
        )

        self._client = client
        self._app = config.app

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
