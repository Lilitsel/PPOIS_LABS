class FrameBuffer:
    def __init__(self, width: int, height: int, bytes_per_pixel: int = 4):
        self.width = width
        self.height = height
        self.bytes_per_pixel = bytes_per_pixel
        self.frames_swapped: int = 0

    def size_bytes(self) -> int:
        return self.width * self.height * self.bytes_per_pixel

    def swap_buffers(self) -> int:
        self.frames_swapped += 1
        return self.frames_swapped
