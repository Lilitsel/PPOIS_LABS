from computer_system.exceptions.computer_exception import ComputerException


class PeripheralTimeoutException(ComputerException):
    """Raised when an I/O peripheral stops responding."""
