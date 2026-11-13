from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InvalidTourDataException(TravelAgencyException):
    """Некорректные параметры тура, программы или пакета."""
