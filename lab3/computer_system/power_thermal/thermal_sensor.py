class ThermalSensor:
    def __init__(self, sensor_name: str, current_c: float = 35.0, alert_c: float = 85.0):
        self.sensor_name = sensor_name
        self.current_c = current_c
        self.alert_c = alert_c

    def read_celsius(self, new_temp_c: float | None = None) -> float:
        if new_temp_c is not None:
            self.current_c = round(new_temp_c, 1)
        return self.current_c

    def is_overheating(self) -> bool:
        return self.current_c >= self.alert_c
