from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InvalidClientDataException(TravelAgencyException):
    """Некорректные данные клиента или отзыва."""
