from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class CardExpiredException(TravelAgencyException):
    """Срок действия банковской карты истёк."""
