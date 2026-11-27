class RomChip:
    def __init__(self, chip_type: str, size_kb: int, writable: bool = False):
        self.chip_type = chip_type
        self.size_kb = size_kb
        self.writable = writable
        self.firmware_version: str = "1.0.0"

    def update_firmware(self, version: str) -> str:
        if self.writable and version.strip():
            self.firmware_version = version.strip()
        return self.firmware_version
