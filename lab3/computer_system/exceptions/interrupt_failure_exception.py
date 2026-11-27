from computer_system.exceptions.computer_exception import ComputerException


class InterruptFailureException(ComputerException):
    """Raised when hardware interrupt handling fails."""
