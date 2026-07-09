import json
import aio_pika
from pydantic import ValidationError
from src.rideci.application.usesCases.UpdateUserUseCase import UpdateUserUseCase
from src.rideci.domain.dtos.events import UserUpdateDTO
from src.rideci.core.logging import logger

class RabbitMQUserConsumer:
    def __init__(self, connection: aio_pika.RobustConnection, update_user_uc: UpdateUserUseCase):
        self.connection = connection
        self.update_user_use_case = update_user_uc
        self.queue_name = "rideci.user.updated"

    async def start_consuming(self):
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=10) 
        
        queue = await channel.declare_queue(self.queue_name, durable=True)
        logger.info(f"[RabbitMQ] Listening on: {self.queue_name}")
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._process_message(message.body)

    async def _process_message(self, body: bytes):
        try:
            payload = json.loads(body.decode('utf-8'))
            user_dto = UserUpdateDTO(**payload)
            await self.update_user_use_case.execute(user_dto.model_dump())
            
            logger.info(f"[RabbitMQ] User {user_dto.userId} updated successfully.")
            
        except json.JSONDecodeError:
            logger.error("[RabbitMQ] Received non-JSON message, skipping.")
        except ValidationError as ve:
            logger.error(f"[RabbitMQ] Invalid data format received: {ve.json()}")
        except Exception as e:
            logger.exception(f"[RabbitMQ] Unexpected error: {e}")