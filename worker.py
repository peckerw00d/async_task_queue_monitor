import asyncio
import time

import aio_pika

from models import Action, ResultMessage, TaskMessage


class Worker:
    def __init__(
        self,
        connection: aio_pika.abc.AbstractRobustConnection,
        task_queue: str,
        result_queue: str,
    ):
        self.connection = connection
        self.task_queue = task_queue
        self.result_queue = result_queue

    async def start(self):
        async with self.connection:
            channel = await self.connection.channel()
            await channel.set_qos(prefetch_count=10)

            queue = await channel.declare_queue(self.task_queue, auto_delete=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        msg = TaskMessage.model_validate_json(message.body.decode())

                        if msg.action == Action.WAIT:
                            start = time.time()
                            result = await self._process_wait_message(message=msg)
                            end = time.time()
                            duration = end - start
                            msg.duration += duration
                            await self._publish_task_results(
                                message=msg, result=result, channel=channel
                            )

                        elif msg.action == Action.FAIL:
                            start = time.time()
                            result = await self._process_fail_message()
                            end = time.time()
                            duration = end - start
                            msg.duration = duration
                            await self._publish_task_results(
                                message=msg, result=result, channel=channel
                            )

                        else:
                            start = time.time()
                            result = await self._process_ping_message()
                            end = time.time()
                            duration = end - start
                            msg.duration = duration
                            await self._publish_task_results(
                                message=msg, result=result, channel=channel
                            )

    async def _publish_task_results(
        self, message: TaskMessage, result: str, channel: aio_pika.abc.AbstractChannel
    ):
        result_message = ResultMessage(
            task_id=message.task_id,
            status="error" if message.action == Action.FAIL else "success",
            result=result,
            duration=message.duration,
        )
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=result_message.model_dump_json().encode("utf-8"),
                delivery_mode=2,
                content_type="application/json",
            ),
            routing_key=self.result_queue,
        )

    async def _process_wait_message(self, message: TaskMessage):
        await asyncio.sleep(message.duration)
        return "Sleep..."

    async def _process_ping_message(self):
        return "Pong!"

    async def _process_fail_message(self):
        return "Fail!"


if __name__ == "__main__":
    import os

    import dotenv

    dotenv.load_dotenv()
    rabbit_url = os.getenv("RABBITMQ_URL", "amqp://rmuser:rmpassword@localhost:5672/")

    async def run():
        connection = await aio_pika.connect_robust(rabbit_url)
        worker = Worker(
            connection=connection, task_queue="task_queue", result_queue="result_queue"
        )
        await worker.start()

    asyncio.run(run())
