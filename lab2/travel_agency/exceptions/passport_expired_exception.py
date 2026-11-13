from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class PassportExpiredException(TravelAgencyException):
    """Паспорт недействителен на нужную дату."""
