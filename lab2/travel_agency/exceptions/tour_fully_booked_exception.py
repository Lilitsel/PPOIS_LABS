from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class TourFullyBookedException(TravelAgencyException):
    """В туре не осталось свободных мест."""
