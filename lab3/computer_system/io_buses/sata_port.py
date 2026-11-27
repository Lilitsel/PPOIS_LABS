class SataPort:
    def __init__(self, port_number: int, revision: str = "SATA III"):
        self.port_number = port_number
        self.revision = revision
        self.connected_drive: str | None = None

    def connect(self, drive_name: str) -> bool:
        self.connected_drive = drive_name
        return True
