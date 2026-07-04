from src.rideci.infrastructure.repositories.interfaces.InterfaceStatsRepository import InterfaceStatsRepository
from src.rideci.infrastructure.repositories.interfaces.InterfacePredictionEngine import InterfacePredictionEngine

class GetEcoPredictionsUseCase:
    def __init__(self, stats_repo: InterfaceStatsRepository, sklearn_engine: InterfacePredictionEngine, gemini_engine: InterfacePredictionEngine):
        self.stats_repo = stats_repo
        self.sklearn = sklearn_engine  
        self.gemini = gemini_engine    

    async def execute(self, user_id: str) -> dict:
        stats = await self.stats_repo.findByUserId(user_id)
        
        avg_km = stats.totalKmShared / stats.totalTrips if stats.totalTrips > 0 else 0.0

        prediction = await self.sklearn.predict_next_trip_impact(
            average_km=avg_km, 
            expected_passengers=1
        )
        
        
        insight = await self.gemini.generate_personalized_insight(stats, stats.tripsHistory)
        
        return {
            "prediction": prediction,
            "message": insight
        }