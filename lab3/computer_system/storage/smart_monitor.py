class SmartMonitor:
    def __init__(self, device_id: str, temp_c: float = 34.0, power_on_hours: int = 120):
        self.device_id = device_id
        self.temp_c = temp_c
        self.power_on_hours = power_on_hours

    def is_healthy(self) -> bool:
        return self.temp_c < 70.0 and self.power_on_hours < 50000
