from src.rideci.domain.models.UserStats import UserStats
from src.rideci.domain.enums.BadgeType import BadgeType
from src.rideci.infrastructure.repositories.interfaces.InterfaceCacheRepository import InterfaceCacheRepository
from src.rideci.infrastructure.repositories.interfaces.InterfaceStatsRepository import InterfaceStatsRepository
from src.rideci.core.logging import logger

class GetUserMetricsUseCase:
    def __init__(self, stats_repository: InterfaceStatsRepository, cache_repository: InterfaceCacheRepository):
        self.stats_repository = stats_repository
        self.cache_repository = cache_repository

    async def execute(self, user_id: str) -> UserStats:
        # 1. Intentar obtener desde caché (Redis)
        stats = await self.cache_repository.getCachedStats(user_id)
        if stats:
            return stats

        # 2. Intentar obtener desde la base de datos (MongoDB)
        stats = await self.stats_repository.findByUserId(user_id)
        if stats:
            await self.cache_repository.saveCacheStats(user_id, stats)
            return stats

        # 3. Inicializar si es un usuario nuevo
        logger.info(f"Initializing new user profile: {user_id}")
        new_stats = UserStats(
            userId=user_id,
            userName="Estudiante ECI", 
            userType="Estudiante",     
            totalCo2Saved=0.0,
            totalKmShared=0.0,
            totalTrips=0,
            currentBadge=BadgeType.ECO_COMPLIANT,
            mostFrequentRoute="N/A",    
            tripsHistory=[],            
            routesCount={}              
        )
        
        await self.stats_repository.saveUserStats(new_stats.model_dump(), {})
        
        return new_stats