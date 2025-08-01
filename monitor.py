import aio_pika

from models import ResultMessage


class Monitor:
    def __init__(self, connection: aio_pika.abc.AbstractConnection, result_queue: str):
        self.connection = connection
        self.result_queue = result_queue

    async def start(self):
        async with self.connection:
            channel = await self.connection.channel()
            await channel.set_qos(prefetch_count=10)

            queue = await channel.declare_queue(self.result_queue, auto_delete=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await self._log_result_message(message.body)

    async def _log_result_message(self, body: bytes):
        msg = ResultMessage.model_validate_json(body.decode())

        if msg.status == "error":
            print(f"❌ Task {msg.task_id} failed: {msg.result}")

        else:
            print(
                f"✅ Task {msg.task_id} completed in {msg.duration:.2f}s: {msg.result}"
            )


if __name__ == "__main__":
    import asyncio
    import os

    import dotenv

    dotenv.load_dotenv()
    rabbit_url = os.getenv("RABBITMQ_URL", "amqp://rmuser:rmpassword@rabbitmq:5672/")

    async def run():
        connection = await aio_pika.connect_robust(rabbit_url)
        monitor = Monitor(connection=connection, result_queue="result_queue")
        await monitor.start()

    asyncio.run(run())
