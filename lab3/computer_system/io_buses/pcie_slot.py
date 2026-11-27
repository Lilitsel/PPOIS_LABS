from computer_system.exceptions.incompatible_component_exception import IncompatibleComponentException


class PcieSlot:
    def __init__(self, slot_id: str, generation: int = 4, lanes: int = 16):
        self.slot_id = slot_id
        self.generation = generation
        self.lanes = lanes
        self.occupied_by: str | None = None

    def plug_device(self, device_name: str, required_lanes: int) -> bool:
        if required_lanes > self.lanes:
            raise IncompatibleComponentException("Device requires more PCIe lanes than slot provides")
        self.occupied_by = device_name
        return True

    def unplug_device(self) -> str | None:
        prev = self.occupied_by
        self.occupied_by = None
        return prev
