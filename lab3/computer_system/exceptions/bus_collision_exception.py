from computer_system.exceptions.computer_exception import ComputerException


class BusCollisionException(ComputerException):
    """Raised when an internal bus cannot transfer data."""
