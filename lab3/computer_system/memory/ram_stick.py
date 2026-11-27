from computer_system.exceptions.invalid_hardware_config_exception import InvalidHardwareConfigException


class RamStick:
    def __init__(self, slot_index: int, ddr_generation: str, capacity_mb: int, speed_mt_s: int):
        if capacity_mb <= 0 or speed_mt_s <= 0:
            raise InvalidHardwareConfigException("Invalid RAM stick capacity or speed")
        self.slot_index = slot_index
        self.ddr_generation = ddr_generation
        self.capacity_mb = capacity_mb
        self.speed_mt_s = speed_mt_s
        self.ecc_enabled: bool = False

    def capacity_gb(self) -> float:
        return round(self.capacity_mb / 1024.0, 2)

    def enable_ecc(self) -> bool:
        self.ecc_enabled = True
        return True
