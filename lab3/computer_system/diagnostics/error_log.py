from datetime import datetime


class ErrorLog:
    def __init__(self, max_records: int = 200):
        self.max_records = max_records
        self.entries: list[str] = []

    def append_error(self, code: str, message: str, timestamp: datetime) -> int:
        line = f"{timestamp.isoformat()} [{code}] {message}"
        self.entries.append(line)
        if len(self.entries) > self.max_records:
            self.entries.pop(0)
        return len(self.entries)

    def count(self) -> int:
        return len(self.entries)
