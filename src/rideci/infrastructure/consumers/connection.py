import aio_pika
from src.rideci.core.settings import settings

async def get_rabbitmq_connection():
    """Retorna una conexión robusta a RabbitMQ."""
    return await aio_pika.connect_robust(settings.RABBITMQ_URL)