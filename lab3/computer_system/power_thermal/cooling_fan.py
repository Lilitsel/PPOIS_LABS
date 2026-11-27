from computer_system.constants import MIN_FAN_RPM, MAX_FAN_RPM
from computer_system.exceptions.invalid_hardware_config_exception import InvalidHardwareConfigException


class CoolingFan:
    def __init__(self, fan_id: str, diameter_mm: int = 120, rpm: int = 1200):
        self.fan_id = fan_id
        self.diameter_mm = diameter_mm
        self.rpm = rpm

    def set_rpm(self, target_rpm: int) -> int:
        if not (MIN_FAN_RPM <= target_rpm <= MAX_FAN_RPM):
            raise InvalidHardwareConfigException("Fan RPM out of safe range")
        self.rpm = target_rpm
        return self.rpm

    def airflow_cfm(self) -> float:
        return round((self.rpm / 1000.0) * (self.diameter_mm / 120.0) * 32.0, 2)
