from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InvalidDateRangeException(TravelAgencyException):
    """Дата окончания периода раньше даты начала."""
