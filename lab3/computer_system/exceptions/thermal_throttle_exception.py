from computer_system.exceptions.computer_exception import ComputerException


class ThermalThrottleException(ComputerException):
    """Raised when temperature exceeds safe limits."""
