from src.rideci.domain.dtos.events import TripCompletedEvent
from src.rideci.domain.services.CarbonCalculator import CarbonCalculator
from src.rideci.infrastructure.repositories.interfaces.InterfaceCacheRepository import InterfaceCacheRepository
from src.rideci.infrastructure.repositories.interfaces.InterfaceStatsRepository import InterfaceStatsRepository
from src.rideci.application.usesCases.GetUserMetricsUseCase import GetUserMetricsUseCase
from src.rideci.domain.models.UserStats import TripHistoryItem
from src.rideci.core.logging import logger
from pydantic import ValidationError

class ProcessTripEventUseCase:
    def __init__(self, stats_repo: InterfaceStatsRepository, cache_repo: InterfaceCacheRepository, get_user_metrics: GetUserMetricsUseCase):
        self.stats_repository = stats_repo
        self.cache_repository = cache_repo
        self.get_user_metrics = get_user_metrics

    async def execute(self, trip_data: dict) -> None:
        try:
            event = TripCompletedEvent(**trip_data)
        except ValidationError as e:
            logger.error(f"Validation error in received event: {e}")
            return
        
        participants = [event.organizerId] + event.passengersId
        total_people = len(participants)
    
        co2_per_person = CarbonCalculator.calculate_co2_saved(
            km=event.totalKm, 
            vehicle_type=event.vehicleType.value, 
            passengers_count=total_people
        )

        for user_id in participants:
            user_id_str = str(user_id)
            
            user_stats = await self.get_user_metrics.execute(user_id_str)

            new_trip = TripHistoryItem(
                kmShared=event.totalKm,
                passengersCount=total_people,
                typeVehicle=event.vehicleType,
                tripName=event.tripName, 
                co2Saved=co2_per_person,
                recordedUserName=user_stats.userName,
                recordedUserType=user_stats.userType
            )
            
            user_stats.updateMetrics(new_trip)
            
            user_stats.currentBadge = CarbonCalculator.determine_badge(user_stats.totalCo2Saved)

            try:
                stats_dict = user_stats.model_dump(mode='json')
 
                await self.stats_repository.saveUserStats(stats_dict, {})
            
                await self.cache_repository.invalidateCache(user_id_str)
                await self.cache_repository.setLeaderboard(user_id_str, user_stats.totalCo2Saved)
                
                logger.info(f"Trip processed for user {user_id}. CO2: {co2_per_person} kg. Badge: {user_stats.currentBadge}")
            except Exception as e:
                logger.error(f"Critical error persisting data for user {user_id}: {str(e)}")
                raise