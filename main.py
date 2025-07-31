import asyncio
import os

import aio_pika
import dotenv

from monitor import Monitor
from producer import Producer
from worker import Worker

dotenv.load_dotenv()

rabbit_url = os.getenv("RABBITMQ_URL")


async def main() -> None:
    connection = await aio_pika.connect_robust(
        "amqp://rmuser:rmpassword@localhost:5672/"
    )
    task_queue = "task_queue"
    result_queue = "result_queue"
    producer = Producer(connection=connection, task_queue=task_queue)
    worker = Worker(
        connection=connection, task_queue=task_queue, result_queue=result_queue
    )
    monitor = Monitor(connection=connection, result_queue=result_queue)

    await asyncio.gather(producer.start(), worker.start(), monitor.start())


if __name__ == "__main__":
    asyncio.run(main())
