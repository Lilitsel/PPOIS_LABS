class AcpiTable:
    def __init__(self, signature: str, revision: int = 2, oem_id: str = "SYS"):
        self.signature = signature
        self.revision = revision
        self.oem_id = oem_id
        self.checksum_valid: bool = True

    def verify_checksum(self) -> bool:
        return self.checksum_valid
