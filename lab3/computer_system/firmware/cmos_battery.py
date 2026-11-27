class CmosBattery:
    def __init__(self, voltage_v: float = 3.0):
        self.voltage_v = voltage_v
        self.time_drift_sec: int = 0

    def is_healthy(self) -> bool:
        return self.voltage_v >= 2.7

    def record_drift(self, seconds: int) -> int:
        self.time_drift_sec += seconds
        return self.time_drift_sec
