from computer_system.exceptions.post_check_failed_exception import PostCheckFailedException


class PostChecker:
    def __init__(self):
        self.checks_run: list[str] = []

    def run_self_test(self, cpu_ok: bool, ram_ok: bool, gpu_ok: bool) -> bool:
        self.checks_run = ["CPU", "RAM", "GPU"]
        if not (cpu_ok and ram_ok and gpu_ok):
            raise PostCheckFailedException("POST failed on hardware component")
        return True
