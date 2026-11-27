class Alu:
    def __init__(self, width_bits: int = 64):
        self.width_bits = width_bits
        self.zero_flag: bool = False
        self.carry_flag: bool = False
        self.operations_count: int = 0

    def add_values(self, left: int, right: int) -> int:
        self.operations_count += 1
        result = left + right
        self.zero_flag = (result == 0)
        self.carry_flag = result.bit_length() > self.width_bits
        return result

    def bitwise_and(self, left: int, right: int) -> int:
        self.operations_count += 1
        result = left & right
        self.zero_flag = (result == 0)
        return result
