from computer_system.exceptions.segmentation_fault_exception import SegmentationFaultException


class VirtualMemoryUnit:
    def __init__(self, page_size_bytes: int = 4096, max_virtual_address: int = 10**9):
        self.page_size_bytes = page_size_bytes
        self.max_virtual_address = max_virtual_address
        self.page_table: dict[int, int] = {}

    def map_page(self, virt_page: int, phys_frame: int) -> int:
        self.page_table[virt_page] = phys_frame
        return phys_frame

    def translate_address(self, virtual_addr: int) -> int:
        if virtual_addr < 0 or virtual_addr >= self.max_virtual_address:
            raise SegmentationFaultException("Virtual address out of bounds")
        page = virtual_addr // self.page_size_bytes
        offset = virtual_addr % self.page_size_bytes
        frame = self.page_table.get(page, page)
        return frame * self.page_size_bytes + offset
