import json
import aio_pika
from pydantic import ValidationError
from src.rideci.application.usesCases.ProcessTripEventUseCase import ProcessTripEventUseCase
from src.rideci.core.logging import logger

class RabbitMQTripConsumer:
    def __init__(self, connection: aio_pika.RobustConnection, process_trip_uc: ProcessTripEventUseCase):
        self.connection = connection
        self.process_trip_use_case = process_trip_uc
        self.queue_name = "rideci.trips.finished.queue"

    async def start_consuming(self):
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        exchange = await channel.declare_exchange(
            "travel.exchange", 
            aio_pika.ExchangeType.TOPIC, 
            durable=True
        )
        
        queue = await channel.declare_queue(self.queue_name, durable=True)
        
        await queue.bind(exchange, routing_key="travel.completed")
        
        logger.info(f"[RabbitMQ] Worker listo y escuchando en: {self.queue_name}")
        

    async def _process_message(self, body: bytes):
        try:
            data = json.loads(body.decode('utf-8'))
            await self.process_trip_use_case.execute(trip_data=data)
        except ValidationError as ve:
            logger.error(f"[RabbitMQ] Error de validación en evento: {ve}")
        except Exception as e:
            logger.error(f"[RabbitMQ] Error crítico en worker de viajes: {e}")