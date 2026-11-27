from computer_system.constants import MIN_CLOCK_MHZ, MAX_CLOCK_MHZ, MAX_CPU_TEMP_C
from computer_system.exceptions.invalid_hardware_config_exception import InvalidHardwareConfigException
from computer_system.exceptions.thermal_throttle_exception import ThermalThrottleException


class Processor:
    def __init__(self, model: str, architecture: str, cores: int, threads: int, base_clock_mhz: int, tdp_watts: int):
        if cores <= 0 or threads < cores or not (MIN_CLOCK_MHZ <= base_clock_mhz <= MAX_CLOCK_MHZ):
            raise InvalidHardwareConfigException("Invalid CPU core or clock specification")
        self.model = model
        self.architecture = architecture
        self.cores = cores
        self.threads = threads
        self.base_clock_mhz = base_clock_mhz
        self.current_clock_mhz = base_clock_mhz
        self.tdp_watts = tdp_watts
        self.temperature_c: float = 38.0
        self.load_percent: float = 5.0

    def set_clock_mhz(self, mhz: int) -> int:
        if not (MIN_CLOCK_MHZ <= mhz <= MAX_CLOCK_MHZ):
            raise InvalidHardwareConfigException("Clock frequency out of supported range")
        self.current_clock_mhz = mhz
        return self.current_clock_mhz

    def update_workload(self, load_percent: float, ambient_c: float = 22.0) -> float:
        self.load_percent = max(0.0, min(100.0, load_percent))
        self.temperature_c = round(ambient_c + (self.load_percent / 100.0) * (self.tdp_watts * 0.35), 1)
        if self.temperature_c > MAX_CPU_TEMP_C:
            raise ThermalThrottleException("CPU exceeded maximum safe temperature")
        return self.temperature_c

    def compute_flops_giga(self) -> float:
        return round(self.cores * (self.current_clock_mhz / 1000.0) * 8.0, 2)
