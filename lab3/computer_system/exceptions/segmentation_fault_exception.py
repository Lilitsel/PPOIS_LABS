from computer_system.exceptions.computer_exception import ComputerException


class SegmentationFaultException(ComputerException):
    """Raised on invalid memory address access."""
