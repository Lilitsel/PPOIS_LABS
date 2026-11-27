from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class EmployeeNotFoundException(TravelAgencyException):
    """Сотрудник не найден в филиале."""
