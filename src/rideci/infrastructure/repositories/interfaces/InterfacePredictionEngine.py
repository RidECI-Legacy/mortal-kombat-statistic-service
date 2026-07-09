from abc import ABC, abstractmethod

class InterfacePredictionEngine(ABC):
    @abstractmethod
    def train_model(self, historical_trips: list) -> None:
        """Entrena el modelo de machine learning con el histórico de viajes."""
        pass

    @abstractmethod
    def predict_next_trip_impact(self, average_km: float, expected_passengers: int) -> float:
        """Predice el CO2 que se salvará en el próximo viaje basándose en patrones."""
        pass
    
    @abstractmethod
    async def generate_personalized_insight(self, user_stats, trips_history) -> str:
        """Genera un consejo o mensaje motivacional para el usuario."""
        pass