import asyncio

import aiokafka

from fasteda import entity

from . import config, interface


class Consumer:
    def __init__(
        self,
        config: config.Consumer,
    ):
        client = aiokafka.AIOKafkaConsumer(
            *config.topics,
            **config.aiokafka.model_dump(),
            enable_auto_commit=False,
        )

        self._client = client
        self._app = config.app

    async def run(self):
        async with self._client, self._app:
            async for msg in self._client:
                await asyncio.shield(self.handle(msg))

    async def handle(self, msg: interface.ConsumerRecordType) -> None:
        if msg.value is None:
            raise ValueError("Ivalid message")

        event = entity.Event(
            topic=msg.topic,
            headers=dict(msg.headers),
            body=msg.value,
        )

        await self._app.handle(event)
        await self._client.commit()
