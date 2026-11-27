from computer_system.exceptions.storage_device_exception import StorageDeviceException


class SsdDrive:
    def __init__(self, device_id: str, protocol: str, capacity_gb: int, wear_level_percent: int = 0):
        if capacity_gb <= 0:
            raise StorageDeviceException("SSD capacity must be positive")
        self.device_id = device_id
        self.protocol = protocol
        self.capacity_gb = capacity_gb
        self.wear_level_percent = max(0, min(100, wear_level_percent))
        self.blocks: dict[int, str] = {}

    def write_block(self, lba: int, payload: str) -> int:
        if lba < 0 or self.wear_level_percent >= 100:
            raise StorageDeviceException("Cannot write to SSD block")
        self.blocks[lba] = payload
        return len(self.blocks)

    def read_block(self, lba: int) -> str:
        if lba not in self.blocks:
            raise StorageDeviceException("LBA block not found")
        return self.blocks[lba]

    def trim_blocks(self, lbas: list[int]) -> int:
        removed = 0
        for b in lbas:
            if b in self.blocks:
                del self.blocks[b]
                removed += 1
        return removed
