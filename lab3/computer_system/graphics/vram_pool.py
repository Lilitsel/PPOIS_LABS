class VramPool:
    def __init__(self, total_mb: int):
        self.total_mb = total_mb
        self.reserved_mb: int = 0

    def reserve(self, mb: int) -> int:
        if mb > 0 and self.reserved_mb + mb <= self.total_mb:
            self.reserved_mb += mb
        return self.reserved_mb

    def available_mb(self) -> int:
        return self.total_mb - self.reserved_mb
