class DiagnosticSession:
    def __init__(self, session_id: str, target_hostname: str):
        self.session_id = session_id
        self.target_hostname = target_hostname
        self.passed_tests: int = 0

    def record_pass(self) -> int:
        self.passed_tests += 1
        return self.passed_tests
