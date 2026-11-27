from computer_system.power_thermal.thermal_sensor import ThermalSensor


class HardwareMonitor:
    def __init__(self):
        self.sensors: dict[str, ThermalSensor] = {}

    def register_sensor(self, sensor: ThermalSensor) -> int:
        self.sensors[sensor.sensor_name] = sensor
        return len(self.sensors)

    def any_overheating(self) -> bool:
        return any(s.is_overheating() for s in self.sensors.values())
