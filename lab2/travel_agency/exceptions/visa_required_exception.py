from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class VisaRequiredException(TravelAgencyException):
    """Для въезда нужна действующая виза."""
