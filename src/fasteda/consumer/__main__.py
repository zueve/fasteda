import asyncio

import aiokafka
import click

from . import config, consumer


@click.command()
@click.option("--app", help='App module like "myapp.app"')
@click.option("--topics", multiple=True, help='Topics like "topic1"')
def run(**kwargs):
    consumer_config = config.Consumer.from_env(**kwargs)
    aiokafka_config = config.AIOKafka.from_env()

    async def run():
        aiokafka_consumer = aiokafka.AIOKafkaConsumer(
            *consumer_config.topics, **aiokafka_config.model_dump()
        )
        consumer_ = consumer.Consumer(consumer_config, aiokafka_consumer)
        await consumer_.run()

    asyncio.run(run())


if __name__ == "__main__":
    run()
