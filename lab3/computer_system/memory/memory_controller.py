from computer_system.memory.ram_stick import RamStick
from computer_system.exceptions.memory_allocation_exception import MemoryAllocationException


class MemoryController:
    def __init__(self, channels: int = 2, max_speed_mt_s: int = 6000):
        self.channels = channels
        self.max_speed_mt_s = max_speed_mt_s
        self.sticks: list[RamStick] = []

    def attach_stick(self, stick: RamStick) -> int:
        if stick.speed_mt_s > self.max_speed_mt_s:
            raise MemoryAllocationException("RAM speed exceeds controller limit")
        self.sticks.append(stick)
        return len(self.sticks)

    def total_ram_mb(self) -> int:
        return sum(s.capacity_mb for s in self.sticks)
