class RaidArray:
    def __init__(self, raid_level: str, disk_count: int, disk_size_gb: int):
        self.raid_level = raid_level
        self.disk_count = disk_count
        self.disk_size_gb = disk_size_gb

    def usable_capacity_gb(self) -> int:
        if self.raid_level == "RAID1":
            return self.disk_size_gb
        if self.raid_level == "RAID5" and self.disk_count > 1:
            return (self.disk_count - 1) * self.disk_size_gb
        return self.disk_count * self.disk_size_gb
