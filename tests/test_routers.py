import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from src.rideci.main import app
from src.rideci.domain.models.UserStats import UserStats
from src.rideci.domain.enums.BadgeType import BadgeType


@pytest.mark.asyncio
async def test_process_trip_event_success():
    with patch("src.rideci.infrastructure.adapters.routers.process_trip_uc.execute", new_callable=AsyncMock) as mock:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/stats/process-trip", json={"km": 10})
        assert response.status_code == 202
        mock.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_my_stats():
    stats = UserStats(
        userId="1", userName="test", userType="Estudiante", 
        totalCo2Saved=10.0, totalKmShared=5.0, totalTrips=1, 
        currentBadge=BadgeType.ECO_COMPLIANT, mostFrequentDestination="A"
    )
    with patch("src.rideci.infrastructure.adapters.routers.metrics_uc.execute", return_value=stats):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/stats/1?userName=test&userType=Estudiante")
        assert response.status_code == 200
        assert response.json()["userName"] == "test"

@pytest.mark.asyncio
async def test_get_ai_predictions():
    mock_prediction = {"prediction": 2.45, "message": "¡Sigue así!"}
    with patch("src.rideci.infrastructure.adapters.routers.ai_uc.execute", new_callable=AsyncMock, return_value=mock_prediction) as mock:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/stats/1/predictions")
        assert response.status_code == 200
        assert response.json()["prediction"] == 2.45
        mock.assert_awaited_once()

@pytest.mark.asyncio
async def test_export_report_404():
    with patch("src.rideci.infrastructure.adapters.routers.stats_repo.findByUserId", new_callable=AsyncMock, return_value=None):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/stats/999/export/pdf")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Usuario no encontrado"

@pytest.mark.asyncio
async def test_export_report_success():
    mock_user = UserStats(
        userId="1", userName="a", userType="b", 
        totalCo2Saved=10.0, totalKmShared=5.0, totalTrips=1, 
        currentBadge=BadgeType.ECO_COMPLIANT, mostFrequentDestination="D"
    )
    with patch("src.rideci.infrastructure.adapters.routers.stats_repo.findByUserId", new_callable=AsyncMock, return_value=mock_user), \
         patch("src.rideci.infrastructure.adapters.routers.report_uc.execute", new_callable=AsyncMock, return_value="http://s3.link"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/stats/1/export/pdf")
        assert response.status_code == 200
        assert "download_url" in response.json()

@pytest.mark.asyncio
async def test_process_trip_event_error():
    with patch("src.rideci.infrastructure.adapters.routers.process_trip_uc.execute", side_effect=Exception("Error")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/v1/stats/process-trip", json={"km": 10})
        assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_user_co2():
    stats = UserStats(userId="1", userName="test", userType="A", totalCo2Saved=100.0, totalKmShared=10.0, totalTrips=1, currentBadge=BadgeType.ECO_COMPLIANT, mostFrequentDestination="A")
    with patch("src.rideci.infrastructure.adapters.routers.metrics_uc.execute", return_value=stats):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/stats/1/co2")
        assert response.status_code == 200
        assert response.json()["co2_saved_kg"] == 100.0

@pytest.mark.asyncio
async def test_export_report_error():
    mock_user = UserStats(userId="1", userName="a", userType="b", totalCo2Saved=10.0, totalKmShared=5.0, totalTrips=1, currentBadge=BadgeType.ECO_COMPLIANT, mostFrequentDestination="D")
    with patch("src.rideci.infrastructure.adapters.routers.stats_repo.findByUserId", return_value=mock_user), \
         patch("src.rideci.infrastructure.adapters.routers.report_uc.execute", side_effect=Exception("S3 error")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/stats/1/export/pdf")
        assert response.status_code == 500

