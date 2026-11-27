class BootLoader:
    def __init__(self, loader_name: str = "GRUB2", default_os: str = "Linux"):
        self.loader_name = loader_name
        self.default_os = default_os
        self.timeout_sec: int = 5

    def select_os(self, os_name: str) -> str:
        if os_name.strip():
            self.default_os = os_name.strip()
        return self.default_os
