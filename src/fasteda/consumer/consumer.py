import asyncio

import aiokafka

from fasteda import entity

from . import config, interface


class Consumer:
    def __init__(
        self,
        config: config.Consumer,
        client: aiokafka.AIOKafkaConsumer,
    ):
        self._config = config
        self._app = config.app
        self._client = client

    async def run(self):
        await self._client.start()
        await self._app.start()

        try:
            async for msg in self._client:
                await asyncio.shield(self.handle(msg))
        finally:
            await self._app.stop()
            await self._client.stop()

    async def handle(self, msg: interface.ConsumerRecordType) -> None:
        if msg.value is None:
            raise ValueError("Ivalid message")

        event = entity.Event(
            topic=msg.topic,
            headers=dict(msg.headers),
            body=msg.value,
        )

        await self._app.handle(event)

        if self._config.enable_auto_commit:
            await self._client.commit()
