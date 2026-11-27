class PcieLaneAllocator:
    def __init__(self, total_lanes: int = 24):
        self.total_lanes = total_lanes
        self.used_lanes: int = 0

    def allocate_lanes(self, lanes: int) -> int:
        if lanes > 0 and self.used_lanes + lanes <= self.total_lanes:
            self.used_lanes += lanes
        return self.used_lanes

    def free_lanes(self) -> int:
        return self.total_lanes - self.used_lanes
