from travel_agency.exceptions.travel_agency_exception import TravelAgencyException


class InvalidBookingStateException(TravelAgencyException):
    """Операция недопустима в текущем состоянии объекта."""
