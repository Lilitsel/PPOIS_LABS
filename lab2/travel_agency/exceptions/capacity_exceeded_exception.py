from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class CapacityExceededException(TravelAgencyException):
    """Превышена вместимость экскурсии, трансфера или списка ожидания."""
