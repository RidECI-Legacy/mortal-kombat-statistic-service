from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class VehicleType(str, Enum):
    CAR = "CAR"
    MOTORCYCLE = "MOTORCYCLE"
    BUS = "BUS"
    BICYCLE = "BICYCLE"

class TravelType(str, Enum):
    DAILY = 'DAILY'
    OCCASIONAL = 'OCCASIONAL'

class UserType(str, Enum):
    STUDENT = 'STUDENT',
    ADMIN = 'ADMIN',
    TEACHER_ADMINISTRATIVE = 'TEACHER_ADMINISTRATIVE',

class TripCompletedEvent(BaseModel):
    id: Optional[str] = None
    organizerId: int
    driverId: Optional[int] = None  
    vehicleType: VehicleType  
    travelType: TravelType    
    passengersId: List[int]
    totalKm: float
    tripName: Optional[str] = "Viaje sin nombre"

class UserUpdateDTO(BaseModel):
    userId: str
    newName: Optional[str] = None
    newType: UserType