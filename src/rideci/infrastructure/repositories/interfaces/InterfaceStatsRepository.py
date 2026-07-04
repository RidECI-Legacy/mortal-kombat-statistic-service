from abc import ABC, abstractmethod
from typing import Optional
from src.rideci.domain.models.UserStats import UserStats

class InterfaceStatsRepository(ABC):

    @abstractmethod
    async def findByUserId(self, user_id: str) -> Optional[UserStats]:
        """Busca las estadísticas consolidadas de un usuario."""
        pass

    @abstractmethod
    async def saveUserStats(self, stats: UserStats, destinations_dict: dict) -> None:
        """Guarda o actualiza las estadísticas del usuario."""
        pass

    @abstractmethod
    async def getGlobalMetrics(self, period: str) -> dict:
        """Obtiene métricas agregadas globales de la plataforma por período."""
        pass