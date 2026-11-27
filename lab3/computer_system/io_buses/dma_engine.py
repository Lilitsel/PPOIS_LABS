class DmaEngine:
    def __init__(self, channels: int = 8):
        self.channels = channels
        self.completed_transfers: int = 0

    def run_dma_transfer(self, src_addr: int, dst_addr: int, length_bytes: int) -> int:
        if length_bytes > 0 and src_addr >= 0 and dst_addr >= 0:
            self.completed_transfers += 1
        return self.completed_transfers
