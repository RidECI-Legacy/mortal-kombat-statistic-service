import json
from src.rideci.core.logging import logger 
from typing import Optional, List, Dict
from src.rideci.domain.models.UserStats import UserStats
from src.rideci.infrastructure.repositories.interfaces.InterfaceCacheRepository import InterfaceCacheRepository
from src.rideci.core.RedisConfig import RedisConfig

class RedisCacheRepository(InterfaceCacheRepository):
    def __init__(self):
        self.redis_client = RedisConfig.get_connection()

    async def getCachedStats(self, user_id: str) -> Optional[UserStats]:
        try:
            data = await self.redis_client.get(f"stats:{user_id}")
            if not data:
                return None
            return UserStats(**json.loads(data))
        except Exception as e:
            logger.error(f"Error retrieving cache for {user_id}: {e}")
            return None

    async def saveCacheStats(self, user_id: str, stats: UserStats, expire_seconds: int = 3600) -> None:
        try:
            await self.redis_client.set(
                f"stats:{user_id}",
                stats.model_dump_json(),
                ex=expire_seconds
            )
        except Exception as e:
            logger.error(f"Error saving cache for {user_id}: {e}")

    async def invalidateCache(self, user_id: str) -> None:
        await self.redis_client.delete(f"stats:{user_id}")

    async def setLeaderboard(self, user_id: str, score: float) -> None:
        await self.redis_client.zadd("leaderboard:co2", {user_id: score})

    async def getLeaderboard(self, top_n: int = 10) -> List[Dict]:
        leaderboard = await self.redis_client.zrevrange("leaderboard:co2", 0, top_n - 1, withscores=True)
        return [{"userId": user_id.decode('utf-8') if isinstance(user_id, bytes) else user_id, "score": score} 
                for user_id, score in leaderboard]

    async def getCachedInstitutionalStats(self, period: str, user_type: Optional[str]) -> Optional[List[Dict]]:
        """Cachea resultados agregados del dashboard."""
        key = f"stats:inst:{period}:{user_type or 'all'}"
        data = await self.redis_client.get(key)
        return json.loads(data) if data else None

    async def saveCacheInstitutionalStats(self, period: str, user_type: Optional[str], data: List[Dict], expire_seconds: int = 300) -> None:
        """Guarda resultados agregados por 5 minutos."""
        key = f"stats:inst:{period}:{user_type or 'all'}"
        await self.redis_client.set(key, json.dumps(data), ex=expire_seconds)