from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InvalidPromoCodeException(TravelAgencyException):
    """Промокод недействителен или исчерпан."""
