from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class RefundNotAllowedException(TravelAgencyException):
    """Возврат средств невозможен."""
