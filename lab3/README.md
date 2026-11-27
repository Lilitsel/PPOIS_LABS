# Lab 3: Computer System

Object-oriented Python model of a computer system: processor, cores, cache, registers, ALU, motherboard, chassis, PCIe lane allocator, RAM and virtual memory, drives and file system, GPU and display pipeline, I/O buses, power and thermal management, BIOS/UEFI firmware, diagnostics, domain exceptions, and an interactive CLI[cite: 7].

## Summary Statistics

| Metric | Requirement | In Project |
| :--- | :---: | :---: |
| Domain classes | >= 50 | 52 |
| Fields (total) | >= 150 | 196 |
| Meaningful behaviors (public methods) | >= 100 | 168 |
| Associations between classes | >= 30 | 74 |
| Custom exceptions | >= 12 | 15[cite: 7] |

## Classes Description

| Class | Package | Description |
| :--- | :--- | :--- |
| `Computer` | `core` | Top-level computer system orchestrating hardware, firmware, storage, graphics, and diagnostics |
| `Motherboard` | `core` | Main circuit board connecting CPU, memory, firmware, buses, slots, and power |
| `Processor` | `core` | Central processing unit managing cores, caches, registers, and clock generation |
| `CpuCore` | `core` | Individual execution core running instructions and handling interrupts |
| `Alu` | `core` | Arithmetic logic unit performing mathematical and logical operations |
| `RegisterFile` | `core` | Fast processor register set storing operands, results, and control flags |
| `CpuCache` | `core` | High-speed cache memory reducing average memory access latency |
| `ClockGenerator` | `core` | Clock signal generator controlling base/boost frequencies and timing ticks |
| `PcieLaneAllocator` | `core` | Allocates and tracks PCIe lanes across expansion and storage slots |
| `CaseChassis` | `core` | Physical enclosure housing hardware components, cooling fans, and sensors |
| `MemoryController` | `memory` | Coordinates reads, writes, allocations, and virtual memory across RAM/ROM |
| `RamBank` | `memory` | Logical bank grouping RAM modules for address decoding and access |
| `RamStick` | `memory` | Volatile memory module storing active program data and runtime state |
| `RomChip` | `memory` | Non-volatile read-only chip holding low-level firmware code |
| `VirtualMemoryUnit` | `memory` | Translates virtual addresses to physical frames and manages TLB state |
| `TlbEntry` | `memory` | Translation lookaside buffer entry caching virtual-to-physical page mappings |
| `CacheLine` | `memory` | Basic cache block holding a memory tag, data payload, and validity/dirty flags |
| `BiosFirmware` | `firmware` | Low-level firmware managing POST, hardware initialization, and boot flow |
| `CmosBattery` | `firmware` | Backup cell preserving CMOS and firmware settings when power is off |
| `UefiVariable` | `firmware` | Key-value firmware boot or configuration variable |
| `PostChecker` | `firmware` | Runs Power-On Self-Test checks on critical hardware subsystems |
| `BootLoader` | `firmware` | Loads bootable OS/kernel data from storage and transfers control |
| `AcpiTable` | `firmware` | Describes system power and thermal states for OS power management |
| `SystemBus` | `io_buses` | Shared communication bus transferring data and arbitrating device access |
| `InterruptController` | `io_buses` | Routes, masks, and dispatches hardware interrupts to CPU cores |
| `DmaEngine` | `io_buses` | Transfers data directly between I/O devices and memory without heavy CPU load |
| `PcieSlot` | `io_buses` | PCI Express expansion slot for high-bandwidth cards such as GPUs |
| `M2Slot` | `io_buses` | Compact M.2 slot supporting NVMe/SATA storage modules |
| `SataPort` | `io_buses` | Serial ATA interface port for connecting HDD and SSD storage devices |
| `UsbController` | `io_buses` | Universal Serial Bus controller managing attached peripherals and transfers |
| `SerialPort` | `io_buses` | Serial interface for low-level character/byte communication |
| `NetworkInterface` | `io_buses` | Network adapter handling link state and packet/frame transmission |
| `StorageController` | `storage` | Manages block I/O, drives, RAID arrays, and SMART health monitoring |
| `HddDrive` | `storage` | Mechanical magnetic storage drive organized into sectors and partitions |
| `SsdDrive` | `storage` | Solid-state flash drive with page/block I/O and wear tracking |
| `RaidArray` | `storage` | Logical multi-drive array supporting redundancy or striped storage |
| `Partition` | `storage` | Contiguous slice of a drive that can be formatted and mounted |
| `FileSystem` | `storage` | Organizes files, directories, and free space on a mounted partition |
| `SmartMonitor` | `storage` | Monitors drive SMART attributes and reports storage health |
| `PowerSupplyUnit` | `power_thermal` | Supplies regulated electrical power across rails and manages battery state |
| `PowerRail` | `power_thermal` | Individual voltage line (e.g., 3.3V, 5V, 12V) with safety bounds |
| `Battery` | `power_thermal` | Rechargeable battery unit providing charge, voltage, and capacity state |
| `ThermalSensor` | `power_thermal` | Measures component temperature and signals thermal thresholds |
| `FanController` | `power_thermal` | Adjusts cooling fan speeds based on thermal sensor readings |
| `CoolingFan` | `power_thermal` | Active fan spinning to increase airflow and cool components |
| `Heatsink` | `power_thermal` | Passive/assisted thermal spreader dissipating heat from CPU or GPU |
| `HardwareMonitor` | `diagnostics` | Collects telemetry, runs diagnostic checks, and builds health reports |
| `DiagnosticSession` | `diagnostics` | Tracks a diagnostic run along with captured samples and errors |
| `StressTester` | `diagnostics` | Applies simulated load to test stability and thermal behavior |
| `TelemetrySample` | `diagnostics` | Point-in-time snapshot of temperatures, voltages, and load metrics |
| `ErrorLog` | `diagnostics` | Records and filters hardware or runtime diagnostic errors |
| `HealthReport` | `diagnostics` | Summarizes overall component health, findings, and telemetry |
| `Gpu` | `graphics` | Graphics processing unit rendering frames and driving display output |
| `ShaderUnit` | `graphics` | Executes shader programs and graphics compute workloads |
| `VramPool` | `graphics` | Video memory pool managing allocation and release of VRAM blocks |
| `FrameBuffer` | `graphics` | Buffer holding rendered pixel data prior to display presentation |
| `DisplayPipeline` | `graphics` | Processes frames across display stages toward an output connector |
| `DisplayOutput` | `graphics` | Outputs rendered video signal at a given resolution and refresh rate |

## Exceptions

| Exception | When Raised |
| :--- | :--- |
| `ComputerException` | Base domain exception (`Exception`) for computer system errors |
| `PowerOffException` | Operation requires powered-on state while the system or component is off |
| `VoltageOutOfRangeException` | Supply or rail voltage is outside safe operating bounds |
| `ThermalThrottleException` | Component temperature exceeds safe threshold and triggers throttling |
| `InvalidHardwareConfigException` | Hardware configuration or slot/resource setup is invalid |
| `IncompatibleComponentException` | Attached component is incompatible with the host slot, bus, or board |
| `BiosCorruptionException` | BIOS/firmware image or CMOS/UEFI state is corrupted |
| `PostCheckFailedException` | Power-On Self-Test hardware check fails during startup |
| `MemoryAllocationException` | Memory or VRAM allocation fails due to insufficient capacity or invalid request |
| `SegmentationFaultException` | Invalid memory address access or out-of-bounds memory operation |
| `StorageDeviceException` | Storage controller, drive, partition, RAID, or file system operation fails |
| `BusCollisionException` | Contention or collision occurs on a system or I/O bus |
| `InterruptFailureException` | Interrupt handling or dispatch fails in the interrupt controller |
| `PeripheralTimeoutException` | Connected peripheral or I/O device does not respond within timeout |
| `GpuRenderException` | Graphics rendering, shader execution, or display pipeline operation fails |

Table row format: `Class | fields | methods | associations`.
Notation `SubClass <- BaseClass` denotes inheritance. Association means a class is used as a field or method parameter[cite: 1].

## Structure

```text
lab3/
├── computer_system/              # domain package
│   ├── cli/                      # interactive console menu (menu.py)
│   ├── core/                     # CPU, motherboard, chassis, PCIe lane allocator
│   ├── memory/                   # RAM, ROM, cache lines, VMU, TLB, memory controller
│   ├── firmware/                 # BIOS, CMOS battery, UEFI, POST, boot loader, ACPI
│   ├── io_buses/                 # system bus, interrupts, DMA, PCIe, M.2, SATA, USB, serial, NIC
│   ├── storage/                  # HDD, SSD, RAID, partitions, file system, controller, SMART
│   ├── power_thermal/            # PSU, power rails, battery, thermal sensors, fans, heatsink
│   ├── diagnostics/              # hardware monitor, stress tester, telemetry, logs, reports
│   ├── graphics/                 # GPU, shaders, VRAM pool, frame buffer, display pipeline/output
│   ├── exceptions/               # custom domain exceptions (one per module)
│   ├── constants.py              # numeric business-logic constants
│   ├── statuses.py               # state enumerations
│   └── __init__.py
├── tests/                        # unit tests (pytest)
│   ├── __init__.py
│   └── test_computer.py
├── run_cli.py                    # CLI entry point
├── computer_system.pyz           # standalone zipapp artifact
├── requirements-dev.txt          # development and test dependencies
├── setup.cfg                     # flake8, pytest, and coverage configuration
└── README.md
