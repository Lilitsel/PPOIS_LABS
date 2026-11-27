from computer_system.exceptions.computer_exception import ComputerException


class StorageDeviceException(ComputerException):
    """Raised when block/storage read or write fails."""
