from computer_system.exceptions.computer_exception import ComputerException


class BiosCorruptionException(ComputerException):
    """Raised when firmware/BIOS configuration is invalid."""
