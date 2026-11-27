class CacheLine:
    def __init__(self, tag: int, size_bytes: int = 64, dirty: bool = False):
        self.tag = tag
        self.size_bytes = size_bytes
        self.dirty = dirty

    def mark_dirty(self) -> bool:
        self.dirty = True
        return True

    def flush(self) -> bool:
        self.dirty = False
        return False
