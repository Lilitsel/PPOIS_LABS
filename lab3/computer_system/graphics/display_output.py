class DisplayOutput:
    def __init__(self, connector: str, width: int = 1920, height: int = 1080, refresh_hz: int = 60):
        self.connector = connector
        self.width = width
        self.height = height
        self.refresh_hz = refresh_hz
        self.active: bool = False

    def enable_signal(self) -> bool:
        self.active = True
        return True

    def set_mode(self, width: int, height: int, refresh_hz: int) -> str:
        self.width = width
        self.height = height
        self.refresh_hz = refresh_hz
        return f"{self.width}x{self.height}@{self.refresh_hz}Hz"
