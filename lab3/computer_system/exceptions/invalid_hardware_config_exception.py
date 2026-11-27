from computer_system.exceptions.computer_exception import ComputerException


class InvalidHardwareConfigException(ComputerException):
    """Raised when hardware parameters are invalid."""
