class CpuCache:
    def __init__(self, level: str, size_kb: int, line_size_bytes: int = 64):
        self.level = level
        self.size_kb = size_kb
        self.line_size_bytes = line_size_bytes
        self.hits: int = 0
        self.misses: int = 0

    def lookup(self, found: bool) -> float:
        if found:
            self.hits += 1
        else:
            self.misses += 1
        return self.hit_ratio()

    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 1.0
        return round(self.hits / total, 3)
