import pytest
import json
from unittest.mock import AsyncMock
from pydantic import ValidationError
from src.rideci.infrastructure.consumers.RabbitMQTripConsumer import RabbitMQTripConsumer
from src.rideci.infrastructure.consumers.RabbitMQUserConsumer import RabbitMQUserConsumer

# --- Fixtures separadas ---
@pytest.fixture
def trip_consumer():
    return RabbitMQTripConsumer(AsyncMock(), AsyncMock())

@pytest.fixture
def user_consumer():
    return RabbitMQUserConsumer(AsyncMock(), AsyncMock())

# --- Pruebas para RabbitMQTripConsumer ---
@pytest.mark.asyncio
async def test_trip_process_success(trip_consumer):
    data = {"tripId": "123", "organizerId": 1, "passengersId": [2], "totalKm": 10.0}
    await trip_consumer._process_message(json.dumps(data).encode('utf-8'))
    trip_consumer.process_trip_use_case.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_trip_process_invalid_json(trip_consumer):
    await trip_consumer._process_message(b"{ invalid json ")
    trip_consumer.process_trip_use_case.execute.assert_not_awaited()

@pytest.mark.asyncio
async def test_trip_process_validation_error(trip_consumer):
    trip_consumer.process_trip_use_case.execute.side_effect = ValidationError.from_exception_data("Err", [])
    await trip_consumer._process_message(json.dumps({"wrong": "data"}).encode())
    trip_consumer.process_trip_use_case.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_trip_process_critical_exception(trip_consumer):
    trip_consumer.process_trip_use_case.execute.side_effect = Exception("DB Crash")
    await trip_consumer._process_message(json.dumps({"tripId": "123"}).encode())
    trip_consumer.process_trip_use_case.execute.assert_awaited_once()

# --- Pruebas para RabbitMQUserConsumer ---
@pytest.mark.asyncio
async def test_user_process_invalid_json(user_consumer):
    await user_consumer._process_message(b"{ invalid: json ")
    user_consumer.update_user_use_case.execute.assert_not_awaited()

@pytest.mark.asyncio
async def test_user_process_validation_error(user_consumer):
    data = {"userId": "usr_001"} # Falta newType
    await user_consumer._process_message(json.dumps(data).encode('utf-8'))
    user_consumer.update_user_use_case.execute.assert_not_awaited()

@pytest.mark.asyncio
async def test_user_process_wrong_types(user_consumer):
    data = {"userId": 12345, "newType": "INVALID_ROLE"}
    await user_consumer._process_message(json.dumps(data).encode('utf-8'))
    user_consumer.update_user_use_case.execute.assert_not_awaited()