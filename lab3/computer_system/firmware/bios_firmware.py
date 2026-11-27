from computer_system.exceptions.bios_corruption_exception import BiosCorruptionException


class BiosFirmware:
    def __init__(self, vendor: str, version: str, secure_boot: bool = True):
        if not version.strip():
            raise BiosCorruptionException("BIOS version cannot be empty")
        self.vendor = vendor
        self.version = version
        self.secure_boot = secure_boot
        self.settings: dict[str, str] = {"boot_mode": "UEFI", "xmp": "enabled"}

    def set_setting(self, key: str, value: str) -> str:
        self.settings[key] = value
        return self.settings[key]

    def toggle_secure_boot(self, enabled: bool) -> bool:
        self.secure_boot = enabled
        return self.secure_boot
