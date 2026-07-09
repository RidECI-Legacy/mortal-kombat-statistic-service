from datetime import datetime, timezone
from typing import Optional
from src.rideci.infrastructure.repositories.interfaces.InterfaceStatsRepository import InterfaceStatsRepository
from src.rideci.infrastructure.repositories.interfaces.InterfaceCacheRepository import InterfaceCacheRepository
from src.rideci.domain.dtos.DashboardResponse import InstitutionalDashboard
from src.rideci.core.logging import logger

class InstitutionalStatsUseCase:
    def __init__(self, repository: InterfaceStatsRepository, cache: InterfaceCacheRepository):
        self.repository = repository
        self.cache = cache

    async def execute(self, period: str, user_type: Optional[str] = None) -> InstitutionalDashboard:
        """
        Retrieves institutional stats with a Cache-Aside strategy.
        """
        valid_periods = {"week": 7, "month": 30, "semester": 180}
        
        if period not in valid_periods:
            logger.warning(f"Periodo inválido: {period}")
            raise ValueError(f"Periodo inválido. Usa: {list(valid_periods.keys())}")
        
        cached_data = await self.cache.getCachedInstitutionalStats(period, user_type)
        
        if cached_data:
            logger.info(f"Cache hit for institutional stats: {period} | Type: {user_type}")
            data = cached_data
        else:
            logger.info(f"Cache miss, fetching from MongoDB: {period} | Type: {user_type}")
            data = await self.repository.getInstitutionalStats(period, user_type)
            
            if data:
                await self.cache.saveCacheInstitutionalStats(period, user_type, data)
        
        return InstitutionalDashboard(
            status="success",
            metadata={
                "period": period,
                "user_type": user_type or "all",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "cache" if cached_data else "database"
            },
            results=data if data else []
        )