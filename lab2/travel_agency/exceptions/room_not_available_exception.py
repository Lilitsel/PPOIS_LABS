from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class RoomNotAvailableException(TravelAgencyException):
    """Нет свободного подходящего номера."""
