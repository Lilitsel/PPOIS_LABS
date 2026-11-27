from computer_system.statuses import ComponentHealth


class HealthReport:
    def __init__(self, system_label: str):
        self.system_label = system_label
        self.subsystem_health: dict[str, ComponentHealth] = {}

    def set_health(self, subsystem: str, status: ComponentHealth) -> ComponentHealth:
        self.subsystem_health[subsystem] = status
        return status

    def all_healthy(self) -> bool:
        return all(st == ComponentHealth.HEALTHY for st in self.subsystem_health.values())
