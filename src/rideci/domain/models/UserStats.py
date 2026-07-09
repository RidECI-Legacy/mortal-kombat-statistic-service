from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone
from src.rideci.domain.enums.BadgeType import BadgeType

class TripHistoryItem(BaseModel):
    kmShared: float
    passengersCount: int
    tripName: str = "Viaje sin nombre"
    typeVehicle: str
    co2Saved: float
    recordedUserName: Optional[str] = None
    recordedUserType: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserStats(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    userId: str
    userName: str
    userType: str
    totalCo2Saved: float
    totalKmShared: float
    totalTrips: int
    currentBadge: BadgeType
    mostFrequentRoute: str = "N/A"
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tripsHistory: List[TripHistoryItem] = []
    routesCount: Dict[str, int] = {}

    def updateMetrics(self, trip_data: TripHistoryItem) -> None:
        """Actualiza las métricas del usuario tras un viaje."""
        if trip_data.kmShared < 0 or trip_data.co2Saved < 0:
            raise ValueError("Las métricas del viaje no pueden ser negativas.")

        self.totalKmShared = round(self.totalKmShared + trip_data.kmShared, 2)
        self.totalCo2Saved = round(self.totalCo2Saved + trip_data.co2Saved, 2)
        self.totalTrips += 1
        
        self.tripsHistory.append(trip_data)
        
        route = trip_data.tripName
        if route != "Viaje sin nombre":
            self.routesCount[route] = self.routesCount.get(route, 0) + 1
            self.mostFrequentRoute = max(self.routesCount, key=self.routesCount.get)
        
        self.lastUpdated = datetime.now(timezone.utc)