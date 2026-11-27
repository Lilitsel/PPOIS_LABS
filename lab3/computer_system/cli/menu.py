"""CLI for interacting with a Computer model (separated from domain)."""

from computer_system.core.processor import Processor
from computer_system.core.motherboard import Motherboard
from computer_system.memory.memory_controller import MemoryController
from computer_system.memory.ram_stick import RamStick
from computer_system.storage.storage_controller import StorageController
from computer_system.storage.ssd_drive import SsdDrive
from computer_system.graphics.gpu import Gpu
from computer_system.power_thermal.power_supply_unit import PowerSupplyUnit
from computer_system.firmware.bios_firmware import BiosFirmware
from computer_system.core.computer import Computer


def build_demo_computer() -> Computer:
    cpu = Processor("Ryzen 7 7800X3D", "x86_64", 8, 16, 4200, 120)
    board = Motherboard("B650", "AM5", "ATX", 4, 4, 3)
    board.install_cpu(cpu, "AM5")
    mem = MemoryController(channels=2, max_speed_mt_s=6400)
    mem.attach_stick(RamStick(0, "DDR5", 16384, 6000))
    mem.attach_stick(RamStick(1, "DDR5", 16384, 6000))
    stor = StorageController("PCIe Gen4", max_lanes=4)
    stor.attach_ssd(SsdDrive("NVME-0", "NVMe", 1000))
    gpu = Gpu("RTX 4070", 12288, 7168, 2475, 200)
    psu = PowerSupplyUnit("RM750", 750, "80+ Gold")
    bios = BiosFirmware("AMI", "2.10", secure_boot=True)
    return Computer("Workstation-01", cpu, board, mem, stor, gpu, psu, bios)


def run_cli(input_func=input, output_func=print) -> None:
    pc = build_demo_computer()
    while True:
        output_func("\n=== Computer System CLI ===")
        output_func("1. Power ON computer")
        output_func("2. Simulate CPU load (75%)")
        output_func("3. Show system summary")
        output_func("4. Power OFF computer")
        output_func("0. Exit")
        choice = input_func("Select option: ").strip()
        if choice == "1":
            output_func(f"State: {pc.power_on().value}")
        elif choice == "2":
            temp = pc.cpu.update_workload(75.0)
            output_func(f"CPU temp: {temp} C")
        elif choice == "3":
            output_func(pc.system_summary())
        elif choice == "4":
            output_func(f"State: {pc.power_off().value}")
        elif choice == "0":
            break
        else:
            output_func("Invalid option")
