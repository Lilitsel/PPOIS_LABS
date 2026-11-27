class FanController:
    def __init__(self, curve_mode: str = "standard"):
        self.curve_mode = curve_mode
        self.duty_percent: int = 40

    def compute_duty(self, temp_c: float) -> int:
        if temp_c >= 85:
            self.duty_percent = 100
        elif temp_c >= 65:
            self.duty_percent = 70
        else:
            self.duty_percent = 40
        return self.duty_percent
