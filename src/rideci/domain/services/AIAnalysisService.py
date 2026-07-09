import google.generativeai as genai
from src.rideci.core.settings import settings

class AIAnalysisService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-3.5-flash')

    async def analyze(self, data_str: str, badge_name: str) -> str:
        prompt = (
            f"Analiza los siguientes datos: {data_str}. "
            f"Medalla actual del usuario: {badge_name}. "
            f"Genera un reporte corto en formato HTML usando etiquetas <h3> y <ul>. "
            f"NO incluyas etiquetas <html>, <head> o <body>, solo el contenido interior."
        )
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"<p>No fue posible generar el análisis en este momento: {str(e)}</p>"