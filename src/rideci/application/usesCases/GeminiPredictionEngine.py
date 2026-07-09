import google.generativeai as genai
from src.rideci.core.settings import settings
from src.rideci.core.logging import logger
from src.rideci.infrastructure.repositories.interfaces.InterfacePredictionEngine import InterfacePredictionEngine

class GeminiPredictionEngine(InterfacePredictionEngine):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-3.5-flash')

    async def train_model(self, historical_trips: list) -> None:
        """Implementación obligatoria del contrato de la interfaz."""
        logger.info("[Gemini Engine] Motor listo. No requiere re-entrenamiento para insights.")

    async def predict_next_trip_impact(self, average_km: float, expected_passengers: int) -> float:
        """Cálculo matemático para asegurar precisión técnica."""
        impact = average_km * 0.19 * (1 + expected_passengers * 0.1)
        return round(impact, 2)

    async def generate_personalized_insight(self, user_stats, trips_history) -> str:
        """Genera el insight motivacional de forma asíncrona."""
        history_str = str(trips_history[-3:]) if trips_history else "Sin viajes recientes"
        contexto_prompt = (
            f"Actúa como un asistente experto en sostenibilidad de la ECI.\n"
            f"Analiza al usuario {user_stats.userName}:\n"
            f"- Total de viajes: {user_stats.totalTrips}\n"
            f"- CO2 mitigado: {user_stats.totalCo2Saved} kg\n"
            f"- Destino recurrente: {user_stats.mostFrequentRoute}\n"
            f"Historial reciente: {history_str}\n\n"
            f"Genera un insight corto (máximo 2 líneas) para mejorar su impacto."
        )

        try:
            response = await self.model.generate_content_async(contexto_prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"[Gemini Error] {str(e)}")
            return "¡Excelente trabajo! Sigue compartiendo tu viaje para reducir la huella de carbono en la Escuela."