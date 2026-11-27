from computer_system.statuses import PowerState, BootStage
from computer_system.core.processor import Processor
from computer_system.core.motherboard import Motherboard
from computer_system.memory.memory_controller import MemoryController
from computer_system.storage.storage_controller import StorageController
from computer_system.graphics.gpu import Gpu
from computer_system.power_thermal.power_supply_unit import PowerSupplyUnit
from computer_system.firmware.bios_firmware import BiosFirmware
from computer_system.exceptions.power_off_exception import PowerOffException


class Computer:
    def __init__(
        self,
        hostname: str,
        cpu: Processor,
        motherboard: Motherboard,
        memory: MemoryController,
        storage: StorageController,
        gpu: Gpu,
        psu: PowerSupplyUnit,
        bios: BiosFirmware,
    ):
        self.hostname = hostname
        self.cpu = cpu
        self.motherboard = motherboard
        self.memory = memory
        self.storage = storage
        self.gpu = gpu
        self.psu = psu
        self.bios = bios
        self.power_state = PowerState.OFF
        self.boot_stage = BootStage.POWER_ON
        self.uptime_seconds: int = 0

    def power_on(self) -> PowerState:
        self.power_state = PowerState.RUNNING
        self.boot_stage = BootStage.OS_READY
        return self.power_state

    def power_off(self) -> PowerState:
        self.power_state = PowerState.OFF
        self.boot_stage = BootStage.POWER_ON
        return self.power_state

    def sleep(self) -> PowerState:
        if self.power_state != PowerState.RUNNING:
            raise PowerOffException("Computer must be running to enter sleep")
        self.power_state = PowerState.SLEEP
        return self.power_state

    def total_load_watts(self) -> int:
        if self.power_state == PowerState.OFF:
            return 0
        return self.cpu.tdp_watts + self.gpu.tdp_watts + 45

    def system_summary(self) -> str:
        return (
            f"{self.hostname} [{self.power_state.value}] | "
            f"CPU: {self.cpu.model} | RAM: {self.memory.total_ram_mb()}MB | "
            f"GPU: {self.gpu.model}"
        )
