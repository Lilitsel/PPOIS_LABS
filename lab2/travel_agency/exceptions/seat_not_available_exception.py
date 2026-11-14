from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class SeatNotAvailableException(TravelAgencyException):
    """Место в самолёте занято или не существует."""
