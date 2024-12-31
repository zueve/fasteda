import asyncio

import click

from . import config, consumer


@click.command()
@click.option("--app", help='App module like "myapp.app"')
@click.option("--bootstrap_servers", help="Kafka servers")
@click.option("--group_id", help="Consumer group_id")
def run(**kwargs):
    consumer_config = config.Consumer.from_env(**kwargs)

    async def run() -> None:
        consumer_ = consumer.Consumer(consumer_config)
        await consumer_.run()

    asyncio.run(run())


if __name__ == "__main__":
    run()
