class RamBank:
    def __init__(self, bank_id: int, rows: int = 1024, cols: int = 256):
        self.bank_id = bank_id
        self.rows = rows
        self.cols = cols
        self.active_row: int | None = None

    def activate_row(self, row_idx: int) -> int:
        self.active_row = row_idx % self.rows
        return self.active_row

    def precharge(self) -> bool:
        self.active_row = None
        return True
