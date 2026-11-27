# Lab 3: Computer System

Object-oriented Python model of a computer system: processor, cores, cache, registers, ALU, motherboard, chassis, PCIe lane allocator, RAM and virtual memory, drives and file system, GPU and display pipeline, I/O buses, power and thermal management, BIOS/UEFI firmware, diagnostics, domain exceptions, and an interactive CLI.

## Summary Statistics

| Metric | Requirement | In Project |
| :--- | :---: | :---: |
| Domain classes | >= 50 | 52 |
| Fields (total) | >= 150 | 196 |
| Meaningful behaviors (public methods) | >= 100 | 168 |
| Associations between classes | >= 30 | 74 |
| Custom exceptions | >= 12 | 15 |

Table row format: `Class | fields | methods | associations`.
Notation `SubClass <- BaseClass` denotes inheritance. Association means a class is used as a field or method parameter.

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
