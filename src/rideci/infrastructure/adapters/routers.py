from typing import Optional
from fastapi import APIRouter, HTTPException, status
from src.rideci.core.logging import logger
from src.rideci.infrastructure.repositories.MongoStatsRepository import MongoStatsRepository
from src.rideci.infrastructure.repositories.RedisCacheRepository import RedisCacheRepository
from src.rideci.infrastructure.storage.S3StorageService import S3StorageService
from src.rideci.application.usesCases.GeminiPredictionEngine import GeminiPredictionEngine
from src.rideci.infrastructure.analytics.SklearnPredictionEngine import SklearnPredictionEngine
from src.rideci.domain.services.AIAnalysisService import AIAnalysisService
from src.rideci.application.usesCases.UpdateUserUseCase import UpdateUserUseCase
from src.rideci.application.usesCases.GetUserMetricsUseCase import GetUserMetricsUseCase
from src.rideci.application.usesCases.GetEcoPredictionsUseCase import GetEcoPredictionsUseCase
from src.rideci.application.usesCases.InstitutionalStatsUseCase import InstitutionalStatsUseCase
from src.rideci.application.usesCases.ReportGeneratorUseCase import ReportGeneratorUseCase
from src.rideci.application.usesCases.ProcessTripEventUseCase import ProcessTripEventUseCase
from src.rideci.domain.models.UserStats import UserStats
from src.rideci.domain.dtos.events import UserUpdateDTO

router = APIRouter(prefix="/api/v1/stats", tags=["Stats"])

stats_repo = MongoStatsRepository()
cache_repo = RedisCacheRepository()
s3_service = S3StorageService()
ai_analysis = AIAnalysisService()
sklearn_engine = SklearnPredictionEngine()
gemini_engine = GeminiPredictionEngine()

metrics_uc = GetUserMetricsUseCase(stats_repo, cache_repo)
update_uc = UpdateUserUseCase(stats_repo, cache_repo)
inst_uc = InstitutionalStatsUseCase(stats_repo, cache_repo)
report_uc = ReportGeneratorUseCase(s3_service, ai_analysis)
process_trip_uc = ProcessTripEventUseCase(stats_repo, cache_repo, metrics_uc)
ai_uc = GetEcoPredictionsUseCase(stats_repo, sklearn_engine, gemini_engine)

@router.get("/institutional")
async def get_institutional_stats(period: str = "month", user_type: Optional[str] = None):
    return await inst_uc.execute(period, user_type)

@router.get("/leaderboard")
async def get_leaderboard(top: int = 10):
    return await cache_repo.getLeaderboard(top)

@router.patch("/update-user")
async def manual_update_user(user_data: UserUpdateDTO):
    await update_uc.execute(user_data.model_dump())
    return {"status": "success"}

@router.post("/process-trip", status_code=status.HTTP_202_ACCEPTED)
async def process_trip_event(trip_data: dict):
    try:
        await process_trip_uc.execute(trip_data)
        return {"status": "success", "message": "Trip processed"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en procesamiento")

@router.get("/{user_id}/co2")
async def get_user_co2(user_id: str):
    stats = await metrics_uc.execute(user_id)
    return {
        "user_id": user_id,
        "co2_saved_kg": stats.totalCo2Saved,
        "equivalences": {
            "trees_planted": round(stats.totalCo2Saved / 20, 2),
            "flights_avoided": round(stats.totalCo2Saved / 250, 2)
        }
    }

@router.get("/{user_id}/predictions")
async def get_ai_predictions(user_id: str):
    return await ai_uc.execute(user_id)

@router.get("/{user_id}/export/{file_format}")
async def export_report(user_id: str, file_format: str):
    user_data = await stats_repo.findByUserId(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    try:
        report_data = [
            {"Metrica": "CO2 Ahorrado (kg)", "Valor": float(user_data.totalCo2Saved)},
            {"Metrica": "KM Compartidos", "Valor": float(user_data.totalKmShared)},
            {"Metrica": "Total Viajes", "Valor": float(user_data.totalTrips)}
        ]
        url = await report_uc.execute(user_id, report_data, user_data.model_dump(), file_format)
        return {"download_url": url}
    except Exception:
        raise HTTPException(status_code=500, detail="Error al generar reporte")

@router.get("/{user_id}", response_model=UserStats)
async def get_my_stats(user_id: str):
    return await metrics_uc.execute(user_id)

# OPCION PREMIUM
@router.get("/find-id/{user_name}")
async def get_user_id_by_name(user_name: str):
    user_id = await stats_repo.findUserIdByUserName(user_name)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Usuario con nombre '{user_name}' no encontrado"
        )
    return {"user_name": user_name, "user_id": user_id}
