from computer_system.exceptions.computer_exception import ComputerException


class PowerOffException(ComputerException):
    """Raised when an operation requires the computer to be powered on."""
