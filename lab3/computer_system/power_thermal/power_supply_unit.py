from computer_system.exceptions.voltage_out_of_range_exception import VoltageOutOfRangeException
from computer_system.exceptions.invalid_hardware_config_exception import InvalidHardwareConfigException


class PowerSupplyUnit:
    def __init__(self, model: str, rated_watts: int, efficiency_rating: str = "80+ Gold"):
        if rated_watts <= 0:
            raise InvalidHardwareConfigException("PSU wattage must be positive")
        self.model = model
        self.rated_watts = rated_watts
        self.efficiency_rating = efficiency_rating
        self.rails_voltage: dict[str, float] = {"+12V": 12.0, "+5V": 5.0, "+3.3V": 3.3}

    def check_rail_voltage(self, rail: str, measured_v: float) -> bool:
        nominal = self.rails_voltage.get(rail)
        if nominal is None or abs(measured_v - nominal) > nominal * 0.08:
            raise VoltageOutOfRangeException(f"Rail {rail} voltage out of tolerance")
        return True

    def max_safe_watts(self) -> float:
        return round(self.rated_watts * 0.85, 1)
