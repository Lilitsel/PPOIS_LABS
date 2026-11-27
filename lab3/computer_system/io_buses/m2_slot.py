class M2Slot:
    def __init__(self, slot_name: str, supports_nvme: bool = True, max_length_mm: int = 80):
        self.slot_name = slot_name
        self.supports_nvme = supports_nvme
        self.max_length_mm = max_length_mm
        self.installed_ssd: str | None = None

    def install_ssd(self, ssd_name: str) -> bool:
        self.installed_ssd = ssd_name
        return True
