from computer_system.exceptions.peripheral_timeout_exception import PeripheralTimeoutException


class UsbController:
    def __init__(self, standard: str = "USB 3.2", port_count: int = 6):
        self.standard = standard
        self.port_count = port_count
        self.connected_devices: list[str] = []

    def attach_device(self, device_name: str) -> int:
        if len(self.connected_devices) >= self.port_count:
            raise PeripheralTimeoutException("No free USB ports available")
        self.connected_devices.append(device_name)
        return len(self.connected_devices)

    def detach_device(self, device_name: str) -> bool:
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)
            return True
        return False
