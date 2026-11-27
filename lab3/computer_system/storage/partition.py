class Partition:
    def __init__(self, label: str, filesystem: str, size_gb: int):
        self.label = label
        self.filesystem = filesystem
        self.size_gb = size_gb
        self.used_gb: int = 0

    def allocate_space(self, gb: int) -> int:
        if gb > 0 and self.used_gb + gb <= self.size_gb:
            self.used_gb += gb
        return self.used_gb

    def free_space_gb(self) -> int:
        return self.size_gb - self.used_gb
