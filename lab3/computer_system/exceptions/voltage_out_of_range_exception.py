from computer_system.exceptions.computer_exception import ComputerException


class VoltageOutOfRangeException(ComputerException):
    """Raised when supply voltage is out of safe range."""
