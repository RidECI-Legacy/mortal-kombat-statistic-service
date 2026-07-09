from src.rideci.domain.dtos.events import UserUpdateDTO
from src.rideci.infrastructure.repositories.interfaces.InterfaceStatsRepository import InterfaceStatsRepository
from src.rideci.infrastructure.repositories.interfaces.InterfaceCacheRepository import InterfaceCacheRepository
from src.rideci.core.logging import logger
from pydantic import ValidationError

class UpdateUserUseCase:
    def __init__(self, stats_repository: InterfaceStatsRepository, cache_repository: InterfaceCacheRepository):
        self.stats_repository = stats_repository
        self.cache_repository = cache_repository

    async def execute(self, user_data: dict) -> None:
        """Updates user profile and invalidates cache to ensure data consistency."""
        try:
            update_data = UserUpdateDTO(**user_data)
            logger.info(f"Updating profile for user: {update_data.userId}")
            
            stats = await self.stats_repository.findByUserId(update_data.userId)
            
            if not stats:
                logger.warning(f"User {update_data.userId} not found for update.")
                raise ValueError(f"User {update_data.userId} not found.")

            if update_data.newName:
                stats.userName = update_data.newName
            if update_data.newType:
                stats.userType = update_data.newType
            
            await self.stats_repository.saveUserStats(stats.model_dump(), {})
            await self.cache_repository.invalidateCache(update_data.userId)
            
            logger.info(f"Profile and cache updated for user {update_data.userId}")
            
        except ValidationError as e:
            logger.error(f"Validation error: {e.json()}")
            raise  
        except Exception as e:
            logger.error(f"Critical error in UpdateUserUseCase: {str(e)}")
            raise