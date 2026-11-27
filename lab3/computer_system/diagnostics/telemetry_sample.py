class TelemetrySample:
    def __init__(self, cpu_temp_c: float, ram_used_mb: int, gpu_load_percent: float):
        self.cpu_temp_c = cpu_temp_c
        self.ram_used_mb = ram_used_mb
        self.gpu_load_percent = gpu_load_percent

    def is_within_limits(self) -> bool:
        return self.cpu_temp_c < 90.0 and self.gpu_load_percent <= 100.0
