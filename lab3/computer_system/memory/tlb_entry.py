class TlbEntry:
    def __init__(self, virtual_page: int, physical_frame: int, executable: bool = False):
        self.virtual_page = virtual_page
        self.physical_frame = physical_frame
        self.executable = executable

    def matches(self, page: int) -> bool:
        return self.virtual_page == page
