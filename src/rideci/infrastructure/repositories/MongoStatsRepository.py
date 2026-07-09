from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any
from src.rideci.core.settings import settings
from src.rideci.domain.models.UserStats import UserStats
from src.rideci.infrastructure.repositories.interfaces.InterfaceStatsRepository import InterfaceStatsRepository

class MongoStatsRepository(InterfaceStatsRepository):
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB_NAME]
        self.collection = self.db["user_stats"]

    async def findByUserId(self, user_id: str) -> Optional[UserStats]:
        document = await self.collection.find_one({"userId": user_id})
        if not document:
            return None
        
        document.pop("_id", None)
        return UserStats(**document)

    async def saveUserStats(self, stats_dict: Dict[str, Any], extra_params: Dict = None) -> None:
        """
        Ahora recibe un dict (stats_dict) directamente del model_dump(),
        lo cual es más eficiente y evita problemas de serialización.
        """
        user_id = str(stats_dict["userId"])
        
        await self.collection.update_one(
            {"userId": user_id},
            {"$set": stats_dict},
            upsert=True
        )

    async def getGlobalMetrics(self, period: str) -> dict:
        count = await self.collection.count_documents({})
        return {"total_users": count, "period": period}

    async def getInstitutionalStats(self, period: str, user_type: Optional[str] = None):
        days_map = {"week": 7, "month": 30, "semester": 180}
        limit_date = datetime.now() - timedelta(days=days_map.get(period, 30))
        
        pipeline = []
        
        if user_type:
            pipeline.append({"$match": {"userType": user_type}})
        
        pipeline.extend([
            {"$unwind": "$tripsHistory"}, 
            {"$match": {"tripsHistory.timestamp": {"$gte": limit_date}}}, 
            {"$group": {
                "_id": None, 
                "totalCo2": {"$sum": "$tripsHistory.co2Saved"},
                "totalTrips": {"$sum": 1} 
            }},
            {"$project": {"_id": 0}} 
        ])
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        return results if results else []
    
    async def findUserIdByUserName(self, user_name: str) -> Optional[str]:
        document = await self.collection.find_one({"userName": user_name}, {"userId": 1, "_id": 0})
        if not document:
            return None
        return document.get("userId")