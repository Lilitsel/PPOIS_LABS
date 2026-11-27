"""Unit tests for Computer domain classes, exceptions, and CLI."""

from datetime import datetime
import pytest

from computer_system.statuses import PowerState, ComponentHealth, BusState
from computer_system.core.processor import Processor
from computer_system.core.cpu_core import CpuCore
from computer_system.core.cpu_cache import CpuCache
from computer_system.core.register_file import RegisterFile
from computer_system.core.alu import Alu
from computer_system.core.motherboard import Motherboard
from computer_system.core.clock_generator import ClockGenerator
from computer_system.core.computer import Computer
from computer_system.core.case_chassis import CaseChassis
from computer_system.core.pcie_lane_allocator import PcieLaneAllocator
from computer_system.memory.ram_stick import RamStick
from computer_system.memory.memory_controller import MemoryController
from computer_system.memory.virtual_memory_unit import VirtualMemoryUnit
from computer_system.memory.ram_bank import RamBank
from computer_system.memory.rom_chip import RomChip
from computer_system.memory.cache_line import CacheLine
from computer_system.memory.tlb_entry import TlbEntry
from computer_system.storage.ssd_drive import SsdDrive
from computer_system.storage.hdd_drive import HddDrive
from computer_system.storage.storage_controller import StorageController
from computer_system.storage.partition import Partition
from computer_system.storage.file_system import FileSystem
from computer_system.storage.raid_array import RaidArray
from computer_system.storage.smart_monitor import SmartMonitor
from computer_system.graphics.gpu import Gpu
from computer_system.graphics.display_output import DisplayOutput
from computer_system.graphics.frame_buffer import FrameBuffer
from computer_system.graphics.shader_unit import ShaderUnit
from computer_system.graphics.vram_pool import VramPool
from computer_system.graphics.display_pipeline import DisplayPipeline
from computer_system.io_buses.system_bus import SystemBus
from computer_system.io_buses.pcie_slot import PcieSlot
from computer_system.io_buses.usb_controller import UsbController
from computer_system.io_buses.interrupt_controller import InterruptController
from computer_system.io_buses.dma_engine import DmaEngine
from computer_system.io_buses.network_interface import NetworkInterface
from computer_system.io_buses.sata_port import SataPort
from computer_system.io_buses.m2_slot import M2Slot
from computer_system.io_buses.serial_port import SerialPort
from computer_system.power_thermal.power_supply_unit import PowerSupplyUnit
from computer_system.power_thermal.battery import Battery
from computer_system.power_thermal.cooling_fan import CoolingFan
from computer_system.power_thermal.heatsink import Heatsink
from computer_system.power_thermal.thermal_sensor import ThermalSensor
from computer_system.power_thermal.power_rail import PowerRail
from computer_system.power_thermal.fan_controller import FanController
from computer_system.firmware.bios_firmware import BiosFirmware
from computer_system.firmware.post_checker import PostChecker
from computer_system.firmware.boot_loader import BootLoader
from computer_system.firmware.cmos_battery import CmosBattery
from computer_system.firmware.uefi_variable import UefiVariable
from computer_system.firmware.acpi_table import AcpiTable
from computer_system.diagnostics.hardware_monitor import HardwareMonitor
from computer_system.diagnostics.stress_tester import StressTester
from computer_system.diagnostics.error_log import ErrorLog
from computer_system.diagnostics.health_report import HealthReport
from computer_system.diagnostics.telemetry_sample import TelemetrySample
from computer_system.diagnostics.diagnostic_session import DiagnosticSession
from computer_system.cli.menu import run_cli
from computer_system.exceptions.incompatible_component_exception import IncompatibleComponentException
from computer_system.exceptions.power_off_exception import PowerOffException
from computer_system.exceptions.thermal_throttle_exception import ThermalThrottleException
from computer_system.exceptions.segmentation_fault_exception import SegmentationFaultException
from computer_system.exceptions.post_check_failed_exception import PostCheckFailedException


def test_core_memory_and_computer():
    cpu = Processor("Core i7-14700K", "x86_64", 20, 28, 3400, 125)
    assert cpu.set_clock_mhz(5200) == 5200
    assert cpu.compute_flops_giga() > 0
    assert cpu.update_workload(50.0) < 95.0
    with pytest.raises(ThermalThrottleException):
        cpu.update_workload(100.0, ambient_c=80.0)

    core = CpuCore(0, 5600, has_avx512=True)
    core.assign_thread(101)
    assert core.run_cycles(500) == 500
    assert core.release_core() is True

    cache = CpuCache("L3", 32768)
    assert cache.lookup(True) == 1.0
    assert cache.lookup(False) == 0.5

    regs = RegisterFile()
    regs.write_reg("rax", 42)
    assert regs.read_reg("rax") == 42
    assert regs.advance_pc(4) == 4

    alu = Alu()
    assert alu.add_values(10, 20) == 30
    assert alu.bitwise_and(0b1100, 0b1010) == 0b1000

    board = Motherboard("Z790", "LGA1700", "ATX", 4, 6, 4)
    assert board.install_cpu(cpu, "LGA1700") is True
    assert board.has_cpu() is True
    with pytest.raises(IncompatibleComponentException):
        board.install_cpu(cpu, "AM5")

    clk = ClockGenerator()
    assert clk.adjust_multiplier(40.0) == 4000.0

    stick = RamStick(0, "DDR5", 16384, 5600)
    assert stick.capacity_gb() == 16.0
    assert stick.enable_ecc() is True
    mem_ctrl = MemoryController(max_speed_mt_s=6000)
    assert mem_ctrl.attach_stick(stick) == 1
    assert mem_ctrl.total_ram_mb() == 16384

    vmu = VirtualMemoryUnit()
    vmu.map_page(1, 5)
    assert vmu.translate_address(4096 + 12) == 5 * 4096 + 12
    with pytest.raises(SegmentationFaultException):
        vmu.translate_address(-1)

    bank = RamBank(0)
    assert bank.activate_row(3) == 3
    assert bank.precharge() is True

    rom = RomChip("UEFI", 16384, writable=True)
    assert rom.update_firmware("1.2.0") == "1.2.0"

    cl = CacheLine(10, dirty=True)
    assert cl.flush() is False
    tlb = TlbEntry(2, 8)
    assert tlb.matches(2) is True

    chassis = CaseChassis("ATX")
    chassis.open_side_panel()
    assert chassis.close_side_panel() is True
    lanes = PcieLaneAllocator()
    lanes.allocate_lanes(16)
    assert lanes.free_lanes() == 8


def test_storage_graphics_buses_power_firmware_diag_and_cli():
    ssd = SsdDrive("SSD-1", "NVMe", 2000)
    assert ssd.write_block(1, "boot_sector") == 1
    assert ssd.read_block(1) == "boot_sector"
    assert ssd.trim_blocks([1]) == 1

    hdd = HddDrive("HDD-1", 7200, 4000)
    assert hdd.seek_sector(100) == 100
    assert hdd.rotational_latency_ms() > 0

    s_ctrl = StorageController("SATA/NVMe")
    assert s_ctrl.attach_ssd(ssd) == 1
    assert s_ctrl.total_ssd_capacity_gb() == 2000

    part = Partition("root", "ext4", 500)
    part.allocate_space(120)
    assert part.free_space_gb() == 380
    fs = FileSystem("ext4", part)
    assert fs.create_file("/vmlinuz", 10) is True
    assert fs.delete_file("/vmlinuz") is True

    raid = RaidArray("RAID1", 2, 1000)
    assert raid.usable_capacity_gb() == 1000
    smart = SmartMonitor("SSD-1")
    assert smart.is_healthy() is True

    gpu = Gpu("RX 7900 XT", 20480, 5376, 2390, 315)
    assert gpu.allocate_vram(4096) == 4096
    assert gpu.release_vram(1024) == 3072
    assert gpu.compute_tflops() > 0

    disp = DisplayOutput("DisplayPort")
    assert disp.enable_signal() is True
    assert disp.set_mode(2560, 1440, 144) == "2560x1440@144Hz"

    fb = FrameBuffer(1920, 1080)
    assert fb.size_bytes() > 0
    assert fb.swap_buffers() == 1

    sh = ShaderUnit(0)
    assert sh.compile_shader("pbr.frag") == 1
    vp = VramPool(8192)
    vp.reserve(2048)
    assert vp.available_mb() == 6144
    dp = DisplayPipeline()
    assert dp.enable_hdr() is True

    bus = SystemBus("FSB")
    assert bus.state == BusState.IDLE
    assert bus.transfer_bytes(1024) == 1024
    assert bus.bandwidth_gbps() > 0

    slot = PcieSlot("PCIEX16_1")
    assert slot.plug_device("GPU", 16) is True
    assert slot.unplug_device() == "GPU"

    usb = UsbController()
    assert usb.attach_device("Keyboard") == 1
    assert usb.detach_device("Keyboard") is True

    irq = InterruptController()
    assert irq.raise_irq(14) == 1
    assert irq.handle_next_irq() == 14

    dma = DmaEngine()
    assert dma.run_dma_transfer(0, 1024, 512) == 1

    nic = NetworkInterface("eth0", "AA:BB:CC:DD:EE:FF")
    assert nic.bring_up() is True
    assert nic.bring_down() is False

    sata = SataPort(1)
    assert sata.connect("HDD-1") is True
    m2 = M2Slot("M2_1")
    assert m2.install_ssd("SSD-1") is True
    ser = SerialPort()
    assert ser.transmit(64) == 64

    psu = PowerSupplyUnit("AX1000", 1000)
    assert psu.check_rail_voltage("+12V", 12.1) is True
    assert psu.max_safe_watts() == 850.0

    bat = Battery(60.0, 80.0)
    bat.discharge(20.0)
    assert bat.recharge(10.0) == 70.0

    fan = CoolingFan("FAN-1")
    assert fan.set_rpm(1500) == 1500
    assert fan.airflow_cfm() > 0

    hs = Heatsink("Copper", 6, 220)
    assert hs.can_dissipate(180) is True

    sens = ThermalSensor("CPU_PKG")
    assert sens.read_celsius(45.0) == 45.0
    assert sens.is_overheating() is False

    rail = PowerRail("+12V", 12.0, 50.0)
    assert rail.draw_current(10.0) == 120.0
    fc = FanController()
    assert fc.compute_duty(72.0) == 70

    bios = BiosFirmware("ASUS", "3.0.1")
    bios.set_setting("boot_order", "NVMe")
    assert bios.toggle_secure_boot(True) is True

    post = PostChecker()
    assert post.run_self_test(True, True, True) is True
    with pytest.raises(PostCheckFailedException):
        post.run_self_test(True, False, True)

    bl = BootLoader()
    assert bl.select_os("Ubuntu") == "Ubuntu"
    cmos = CmosBattery()
    assert cmos.is_healthy() is True
    assert cmos.record_drift(2) == 2
    uefi = UefiVariable("BootCurrent", "0001")
    assert uefi.update_value("0002") == "0002"
    acpi = AcpiTable("DSDT")
    assert acpi.verify_checksum() is True

    hw_mon = HardwareMonitor()
    hw_mon.register_sensor(sens)
    assert hw_mon.any_overheating() is False

    st = StressTester()
    assert st.run_benchmark(10.0, 20.0) > 0

    elog = ErrorLog()
    elog.append_error("E01", "Test warning", datetime(2026, 11, 27, 20, 0))
    assert elog.count() == 1

    hr = HealthReport("PC-1")
    hr.set_health("CPU", ComponentHealth.HEALTHY)
    assert hr.all_healthy() is True

    ts = TelemetrySample(55.0, 8192, 40.0)
    assert ts.is_within_limits() is True
    ds = DiagnosticSession("S-1", "PC-1")
    assert ds.record_pass() == 1

    cpu = Processor("Ryzen 5", "x86_64", 6, 12, 3700, 65)
    board = Motherboard("B550", "AM4", "ATX", 4, 4, 2)
    board.install_cpu(cpu, "AM4")
    mem = MemoryController()
    mem.attach_stick(RamStick(0, "DDR4", 8192, 3200))
    stor = StorageController("NVMe")
    stor.attach_ssd(SsdDrive("S1", "NVMe", 512))
    gpu = Gpu("GTX 1660", 6144, 1408, 1785, 120)
    pc = Computer("PC-Test", cpu, board, mem, stor, gpu, psu, bios)
    with pytest.raises(PowerOffException):
        pc.sleep()
    assert pc.total_load_watts() == 0
    pc.power_on()
    assert pc.total_load_watts() > 0
    assert pc.sleep() == PowerState.SLEEP

    inputs = iter(["1", "2", "3", "4", "9", "0"])
    outputs = []
    run_cli(input_func=lambda _: next(inputs), output_func=outputs.append)
    assert any("Computer System CLI" in line for line in outputs)
