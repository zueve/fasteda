from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

import aiokafka
from aiokafka.structs import OffsetAndMetadata

type PendingOffsets = defaultdict[aiokafka.TopicPartition, int]


class DelayedCommitter:
    def __init__(self, consumer: aiokafka.AIOKafkaConsumer, delay_ms: int):
        self._consumer = consumer
        self._delay = timedelta(milliseconds=delay_ms)
        self._pending_offsets: PendingOffsets = defaultdict(int)
        self._last_commit = datetime.now()

    async def commit(self) -> None:
        offsets = {
            tp: OffsetAndMetadata(offset, "")
            for tp, offset in self._pending_offsets.items()
            if offset
        }
        if offsets:
            await self._consumer.commit(offsets=offsets)
            # Safety remove commited offsets from pending
            for tp, metadata in offsets.items():
                if self._pending_offsets.get(tp, 0) == metadata.offset:
                    del self._pending_offsets[tp]

    async def __aenter__(
        self,
    ) -> Callable[[aiokafka.ConsumerRecord], Awaitable[None]]:
        return self._commit_with_delay

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.commit()

    async def _commit_with_delay(self, msg: aiokafka.ConsumerRecord) -> None:
        topic_patition = aiokafka.TopicPartition(msg.topic, msg.partition)
        self._pending_offsets[topic_patition] = msg.offset + 1

        if datetime.now() > self._last_commit + self._delay:
            await self.commit()
            self._last_commit = datetime.now()


class RebalanceListener(aiokafka.ConsumerRebalanceListener):
    def __init__(self, committer: DelayedCommitter):
        self._committer = committer

    async def on_partitions_revoked(self, revoked) -> None:
        await self._committer.commit()

    async def on_partitions_assigned(self, assigned) -> None:
        pass
