from computer_system.exceptions.invalid_hardware_config_exception import InvalidHardwareConfigException


class RegisterFile:
    def __init__(self, bit_width: int = 64, general_count: int = 16):
        if bit_width not in (32, 64):
            raise InvalidHardwareConfigException("Unsupported register bit width")
        self.bit_width = bit_width
        self.general_count = general_count
        self.registers: dict[str, int] = {"rax": 0, "rbx": 0, "rcx": 0, "rsp": 0}
        self.program_counter: int = 0

    def write_reg(self, name: str, value: int) -> int:
        self.registers[name] = value
        return self.registers[name]

    def read_reg(self, name: str) -> int:
        return self.registers.get(name, 0)

    def advance_pc(self, offset: int = 4) -> int:
        self.program_counter += offset
        return self.program_counter
