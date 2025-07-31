import asyncio
import random
import uuid

import aio_pika

from models import Action, TaskMessage


class Producer:
    def __init__(
        self, connection: aio_pika.abc.AbstractRobustConnection, task_queue: str
    ):
        self.connection = connection
        self.task_queue = task_queue

    async def _publish_task(self, msg: TaskMessage):
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=msg.model_dump_json().encode("utf-8"),
                delivery_mode=2,
                content_type="application/json",
            ),
            routing_key=self.task_queue,
        )

    async def start(self):
        while True:
            random_action = random.choice(list(Action))
            if random_action == Action.WAIT:
                random_duration = random.randint(1, 5)

            await self._publish_task(
                TaskMessage(
                    task_id=str(uuid.uuid4()),
                    action=random_action,
                    duration=random_duration if random_action == Action.WAIT else None,
                )
            )
            await asyncio.sleep(3)


if __name__ == "__main__":
    import os

    import dotenv

    dotenv.load_dotenv()
    rabbit_url = os.getenv("RABBITMQ_URL", "amqp://rmuser:rmpassword@rabbitmq:5672/")

    async def run():
        connection = await aio_pika.connect_robust(rabbit_url)
        producer = Producer(connection=connection, task_queue="task_queue")
        await producer.start()

    asyncio.run(run())
