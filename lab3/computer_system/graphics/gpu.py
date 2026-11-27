from computer_system.exceptions.gpu_render_exception import GpuRenderException


class Gpu:
    def __init__(self, model: str, vram_mb: int, cuda_or_stream_cores: int, core_clock_mhz: int, tdp_watts: int):
        if vram_mb <= 0 or core_clock_mhz <= 0:
            raise GpuRenderException("Invalid GPU VRAM or clock")
        self.model = model
        self.vram_mb = vram_mb
        self.cuda_or_stream_cores = cuda_or_stream_cores
        self.core_clock_mhz = core_clock_mhz
        self.tdp_watts = tdp_watts
        self.allocated_vram_mb: int = 0

    def allocate_vram(self, mb: int) -> int:
        if mb <= 0 or self.allocated_vram_mb + mb > self.vram_mb:
            raise GpuRenderException("Not enough VRAM available")
        self.allocated_vram_mb += mb
        return self.allocated_vram_mb

    def release_vram(self, mb: int) -> int:
        self.allocated_vram_mb = max(0, self.allocated_vram_mb - mb)
        return self.allocated_vram_mb

    def compute_tflops(self) -> float:
        return round((self.cuda_or_stream_cores * self.core_clock_mhz * 2) / 1e6, 2)
