from src.rideci.domain.enums.BadgeType import BadgeType

class CarbonCalculator:
    CO2_KG_PER_KM = 0.19 
    
    VEHICLE_FACTORS = {
        "CAR": 1.0,
        "MOTORCYCLE": 0.5,
        "ELECTRIC": 0.2,
        "BUS": 0.1,      
        "BICYCLE": 0.05  
    }

    @classmethod
    def calculate_co2_saved(cls, km: float, vehicle_type: str, passengers_count: int) -> float:
        """Calcula el CO2 mitigado en kg basado en la distancia y pasajeros."""
        if km < 0:
            raise ValueError("Los kilómetros compartidos no pueden ser negativos.")
        
        factor = cls.VEHICLE_FACTORS.get(vehicle_type.upper(), 1.0)
        
        return round(km * cls.CO2_KG_PER_KM * factor * (1 + (passengers_count * 0.1)), 2)

    @classmethod
    def determine_badge(cls, total_co2: float) -> BadgeType:
        """Asigna la insignia correspondiente según el impacto acumulado."""
        if total_co2 >= 100.0:
            return BadgeType.RELIABLE_ECODRIVER
        if total_co2 >= 50.0:
            return BadgeType.HERO_OF_THE_AIR
        if total_co2 >= 15.0:
            return BadgeType.GREEN_PASSER
            
        return BadgeType.ECO_COMPLIANT