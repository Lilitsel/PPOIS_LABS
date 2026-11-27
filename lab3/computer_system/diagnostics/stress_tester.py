class StressTester:
    def __init__(self, duration_sec: int = 60):
        self.duration_sec = duration_sec
        self.last_stability_score: int = 0

    def run_benchmark(self, cpu_flops: float, gpu_tflops: float) -> int:
        score = int(round(cpu_flops * 120 + gpu_tflops * 350))
        self.last_stability_score = max(0, score)
        return self.last_stability_score
