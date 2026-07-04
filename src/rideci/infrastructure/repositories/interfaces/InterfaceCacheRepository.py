from abc import ABC, abstractmethod
from typing import Optional
from src.rideci.domain.models.UserStats import UserStats

class InterfaceCacheRepository(ABC):

    @abstractmethod
    async def setLeaderboard(self, user_id: str, score: float) -> None:
        pass

    @abstractmethod
    async def getCachedStats(self, user_id: str) -> Optional[UserStats]:
        pass

    @abstractmethod
    async def getLeaderboard(self, top_n: int = 10) -> list:
        pass

    @abstractmethod
    async def saveCacheStats(self, user_id: str, stats: UserStats, expire_seconds: int = 3600) -> None:
        pass

    @abstractmethod
    async def invalidateCache(self, user_id: str) -> None:
        pass