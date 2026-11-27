from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class BookingNotFoundException(TravelAgencyException):
    """Бронирование не найдено."""
