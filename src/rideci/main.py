import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rideci.core.settings import settings
from src.rideci.infrastructure.adapters.routers import router as stats_router
from src.rideci.core.logging import logger
from src.rideci.infrastructure.storage.S3StorageService import S3StorageService
from src.rideci.infrastructure.consumers.connection import get_rabbitmq_connection
from src.rideci.core.RedisConfig import RedisConfig

app = FastAPI(
    title=settings.APP_NAME,
    description="Servicio encargado de procesar el CO2 mitigado y gestionar las medallas de sostenibilidad.",
    version="1.0.0",
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats_router)

@app.on_event("startup")
async def startup_event():
    logger.info("--- Iniciando diagnósticos de conectividad ---")

    try:
        s3_service = S3StorageService()
        s3_service.s3.head_bucket(Bucket=s3_service.bucket)
        logger.info("✅ Conexión a S3 (Bucket) verificada.")
    except Exception as e:
        logger.error(f"❌ Error crítico conectando a S3: {e}")

    try:
        connection = await get_rabbitmq_connection()
        logger.info("✅ Conexión a RabbitMQ verificada.")
        await connection.close()
    except Exception as e:
        logger.error(f"❌ Error crítico conectando a RabbitMQ: {e}")

    try:
        redis_client = RedisConfig.get_connection()
        await redis_client.ping()
        logger.info("✅ Conexión a Redis verificada.")
    except Exception as e:
        logger.error(f"❌ Error crítico conectando a Redis: {e}")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Microservicio '{settings.APP_NAME}' corriendo con éxito",
        "status": "Healthy"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)