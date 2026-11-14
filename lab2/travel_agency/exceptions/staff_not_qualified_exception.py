from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class StaffNotQualifiedException(TravelAgencyException):
    """Сотрудник не имеет нужной квалификации."""
