class PowerRail:
    def __init__(self, name: str, nominal_v: float, max_amps: float):
        self.name = name
        self.nominal_v = nominal_v
        self.max_amps = max_amps
        self.current_amps: float = 0.0

    def draw_current(self, amps: float) -> float:
        self.current_amps = max(0.0, min(self.max_amps, amps))
        return round(self.current_amps * self.nominal_v, 2)
