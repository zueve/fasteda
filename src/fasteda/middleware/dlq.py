import logging

import aiokafka
from aiokafka.record.util import Callable

from fasteda import interface

logger = logging.getLogger(__name__)

HEADER_TOPIC_ORIG = "dlq.topic-orig"
HEADER_ATTEMPT = "dlq.attempt"


class DLQ:
    def __init__(
        self,
        dlq_topic: str,
        gen_producer: Callable[[], aiokafka.AIOKafkaProducer],
    ):
        self.topic = dlq_topic
        self.gen_producer = gen_producer
        self._producer: aiokafka.AIOKafkaProducer | None = None

    async def __call__(
        self, event: interface.Event, next_: interface.Handler
    ) -> None:
        if event.topic == self.topic:
            return await next_(event)

        try:
            await next_(event)
        except Exception:
            attempt = int(event.headers.get(HEADER_ATTEMPT, "0")) + 1

            headers = dict(event.headers)
            headers[HEADER_TOPIC_ORIG] = event.topic
            headers[HEADER_ATTEMPT] = str(attempt)

            logger.exception("DLQ:Error processing event, attempt=%s", attempt)

            await self.get_producer().send_and_wait(
                self.topic,
                event.value,
                headers=[(k, v.encode()) for k, v in headers.items()],
            )
        return None

    def get_producer(self) -> aiokafka.AIOKafkaProducer:
        if not self._producer:
            self._producer = self.gen_producer()
        return self._producer
