from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InvalidPaymentDataException(TravelAgencyException):
    """Некорректная сумма, номер карты или валюта."""
