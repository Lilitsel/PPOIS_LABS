class UefiVariable:
    def __init__(self, name: str, value: str, boot_time_only: bool = False):
        self.name = name
        self.value = value
        self.boot_time_only = boot_time_only

    def update_value(self, new_val: str) -> str:
        self.value = new_val
        return self.value
