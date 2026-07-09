import pytest
from src.rideci.domain.services.CarbonCalculator import CarbonCalculator
from src.rideci.domain.enums.BadgeType import BadgeType

def test_calculate_co2_saved_valid_cases():
    assert CarbonCalculator.calculate_co2_saved(10, "CAR", 2) == pytest.approx(2.28)
    
    assert CarbonCalculator.calculate_co2_saved(10, "MOTORCYCLE", 1) == pytest.approx(1.04)
    
    assert CarbonCalculator.calculate_co2_saved(10, "ELECTRIC", 0) == pytest.approx(0.38)
    
    assert CarbonCalculator.calculate_co2_saved(10, "UFO", 0) == pytest.approx(1.9)

def test_calculate_co2_saved_negative_km():
    with pytest.raises(ValueError, match="Los kilómetros compartidos no pueden ser negativos."):
        CarbonCalculator.calculate_co2_saved(-1, "CAR", 1)

@pytest.mark.parametrize("co2, expected_badge", [
    (150.0, BadgeType.RELIABLE_ECODRIVER),
    (100.0, BadgeType.RELIABLE_ECODRIVER),
    (75.0,  BadgeType.HERO_OF_THE_AIR),
    (50.0,  BadgeType.HERO_OF_THE_AIR),
    (20.0,  BadgeType.GREEN_PASSER),
    (15.0,  BadgeType.GREEN_PASSER),
    (5.0,   BadgeType.ECO_COMPLIANT),
])
def test_determine_badge_logic(co2, expected_badge):
    assert CarbonCalculator.determine_badge(co2) == expected_badge