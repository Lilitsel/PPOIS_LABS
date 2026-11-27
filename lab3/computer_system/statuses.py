"""Computer power and component states."""

from enum import Enum


class PowerState(str, Enum):
    OFF = "off"
    STANDBY = "standby"
    RUNNING = "running"
    SLEEP = "sleep"
    HIBERNATE = "hibernate"


class ComponentHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERHEATING = "overheating"
    FAULTY = "faulty"


class BusState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    STALLED = "stalled"
    DISABLED = "disabled"


class BootStage(str, Enum):
    POWER_ON = "power_on"
    POST = "post"
    BIOS_UEFI = "bios_uefi"
    BOOTLOADER = "bootloader"
    OS_READY = "os_ready"
