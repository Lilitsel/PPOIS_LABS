from computer_system.exceptions.storage_device_exception import StorageDeviceException


class HddDrive:
    def __init__(self, device_id: str, rpm: int, capacity_gb: int, platters: int = 2):
        if rpm <= 0 or capacity_gb <= 0:
            raise StorageDeviceException("Invalid HDD RPM or capacity")
        self.device_id = device_id
        self.rpm = rpm
        self.capacity_gb = capacity_gb
        self.platters = platters
        self.head_sector: int = 0

    def seek_sector(self, sector: int) -> int:
        if sector < 0:
            raise StorageDeviceException("Invalid HDD sector")
        self.head_sector = sector
        return self.head_sector

    def rotational_latency_ms(self) -> float:
        return round((60.0 / self.rpm) * 500.0, 2)
