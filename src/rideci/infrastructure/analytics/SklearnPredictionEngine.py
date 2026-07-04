import numpy as np
from sklearn.linear_model import LinearRegression
from src.rideci.infrastructure.repositories.interfaces.InterfacePredictionEngine import InterfacePredictionEngine
from src.rideci.domain.services.CarbonCalculator import CarbonCalculator

class SklearnPredictionEngine(InterfacePredictionEngine):
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False

    async def train_model(self, historical_trips: list) -> None:
        if len(historical_trips) < 3:
            self.is_trained = False
            return

        X = []
        y = []
        for trip in historical_trips:
            km = float(trip.get("kmShared", 0))
            passengers = int(trip.get("passengersCount", 1))
            co2 = float(trip.get("co2Saved", 0))
            X.append([km, passengers])
            y.append(co2)

        self.model.fit(np.array(X), np.array(y))
        self.is_trained = True

    async def predict_next_trip_impact(self, average_km: float, expected_passengers: int) -> float:
        if not self.is_trained:
            return CarbonCalculator.calculate_co2_saved(average_km, "CAR", expected_passengers)
        
        input_data = np.array([[average_km, expected_passengers]])
        prediction = self.model.predict(input_data)[0]
        return round(float(prediction), 2)
    
    async def generate_personalized_insight(self, user_stats, trips_history) -> str:
        raise NotImplementedError("Sklearn no es un motor de lenguaje. Usa Gemini para esto.")