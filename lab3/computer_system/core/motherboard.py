from computer_system.core.processor import Processor
from computer_system.exceptions.incompatible_component_exception import IncompatibleComponentException
from computer_system.exceptions.invalid_hardware_config_exception import InvalidHardwareConfigException


class Motherboard:
    def __init__(self, chipset: str, socket: str, form_factor: str, ram_slots: int, sata_ports: int, m2_slots: int):
        if ram_slots <= 0 or sata_ports < 0 or m2_slots < 0:
            raise InvalidHardwareConfigException("Invalid motherboard slot configuration")
        self.chipset = chipset
        self.socket = socket
        self.form_factor = form_factor
        self.ram_slots = ram_slots
        self.sata_ports = sata_ports
        self.m2_slots = m2_slots
        self.installed_cpu: Processor | None = None

    def install_cpu(self, cpu: Processor, cpu_socket: str) -> bool:
        if cpu_socket.upper() != self.socket.upper():
            raise IncompatibleComponentException("CPU socket does not match motherboard socket")
        self.installed_cpu = cpu
        return True

    def has_cpu(self) -> bool:
        return self.installed_cpu is not None
