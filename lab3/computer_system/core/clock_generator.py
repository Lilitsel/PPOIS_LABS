class ClockGenerator:
    def __init__(self, base_ref_mhz: float = 100.0, multiplier: float = 36.0):
        self.base_ref_mhz = base_ref_mhz
        self.multiplier = multiplier
        self.locked: bool = True

    def target_frequency_mhz(self) -> float:
        return round(self.base_ref_mhz * self.multiplier, 1)

    def adjust_multiplier(self, new_multiplier: float) -> float:
        if new_multiplier > 0:
            self.multiplier = new_multiplier
        return self.target_frequency_mhz()
