import asyncio
from src.rideci.infrastructure.consumers.connection import get_rabbitmq_connection
from src.rideci.infrastructure.consumers.RabbitMQTripConsumer import RabbitMQTripConsumer
from src.rideci.infrastructure.consumers.RabbitMQUserConsumer import RabbitMQUserConsumer

async def main():
    try:
        connection = await get_rabbitmq_connection()
        print("[System] Conectado a RabbitMQ exitosamente.") 
        
        trip_consumer = RabbitMQTripConsumer(connection=connection)
        user_consumer = RabbitMQUserConsumer(connection=connection)
        
        await asyncio.gather(
            trip_consumer.start_consuming(),
            user_consumer.start_consuming()
        )
    except Exception as e:
        print(f"[Error] No se pudo conectar a RabbitMQ: {e}")

if __name__ == "__main__":
    asyncio.run(main())