class Battery:
    def __init__(self, capacity_wh: float, charge_percent: float = 100.0):
        self.capacity_wh = capacity_wh
        self.charge_percent = max(0.0, min(100.0, charge_percent))
        self.cycle_count: int = 0

    def discharge(self, percent: float) -> float:
        self.charge_percent = max(0.0, self.charge_percent - max(0.0, percent))
        return self.charge_percent

    def recharge(self, percent: float) -> float:
        if percent > 0:
            self.charge_percent = min(100.0, self.charge_percent + percent)
            self.cycle_count += 1
        return self.charge_percent
