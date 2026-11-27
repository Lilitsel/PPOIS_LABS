from computer_system.storage.ssd_drive import SsdDrive


class StorageController:
    def __init__(self, interface_name: str, max_lanes: int = 4):
        self.interface_name = interface_name
        self.max_lanes = max_lanes
        self.attached_ssds: list[SsdDrive] = []

    def attach_ssd(self, drive: SsdDrive) -> int:
        self.attached_ssds.append(drive)
        return len(self.attached_ssds)

    def total_ssd_capacity_gb(self) -> int:
        return sum(d.capacity_gb for d in self.attached_ssds)
