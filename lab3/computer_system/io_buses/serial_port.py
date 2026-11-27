class SerialPort:
    def __init__(self, port_name: str = "COM1", baud_rate: int = 115200):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.bytes_sent: int = 0

    def transmit(self, byte_count: int) -> int:
        if byte_count > 0:
            self.bytes_sent += byte_count
        return self.bytes_sent
