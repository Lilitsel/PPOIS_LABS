from computer_system.statuses import BusState
from computer_system.exceptions.bus_collision_exception import BusCollisionException


class SystemBus:
    def __init__(self, bus_name: str, width_bits: int = 64, frequency_mhz: int = 2400):
        self.bus_name = bus_name
        self.width_bits = width_bits
        self.frequency_mhz = frequency_mhz
        self.state = BusState.IDLE
        self.bytes_transferred: int = 0

    def transfer_bytes(self, num_bytes: int) -> int:
        if self.state == BusState.DISABLED:
            raise BusCollisionException("Bus is disabled")
        if num_bytes < 0:
            raise BusCollisionException("Negative byte transfer")
        self.state = BusState.ACTIVE
        self.bytes_transferred += num_bytes
        self.state = BusState.IDLE
        return self.bytes_transferred

    def bandwidth_gbps(self) -> float:
        return round((self.width_bits / 8.0) * (self.frequency_mhz / 1000.0), 2)
