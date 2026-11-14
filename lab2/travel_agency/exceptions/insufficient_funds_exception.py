from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InsufficientFundsException(TravelAgencyException):
    """Недостаточно средств или бонусных баллов."""
