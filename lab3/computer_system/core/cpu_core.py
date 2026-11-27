class CpuCore:
    def __init__(self, core_id: int, max_freq_mhz: int, has_avx512: bool = False):
        self.core_id = core_id
        self.max_freq_mhz = max_freq_mhz
        self.has_avx512 = has_avx512
        self.active_thread_id: int | None = None
        self.instructions_executed: int = 0

    def assign_thread(self, thread_id: int) -> int:
        self.active_thread_id = thread_id
        return self.active_thread_id

    def run_cycles(self, cycles: int) -> int:
        if cycles > 0:
            self.instructions_executed += cycles
        return self.instructions_executed

    def release_core(self) -> bool:
        self.active_thread_id = None
        return True
