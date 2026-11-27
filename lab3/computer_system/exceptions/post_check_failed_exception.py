from computer_system.exceptions.computer_exception import ComputerException


class PostCheckFailedException(ComputerException):
    """Raised when Power-On Self-Test fails."""
