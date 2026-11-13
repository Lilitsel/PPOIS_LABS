"""Собственные исключения предметной области: по одному классу в файле."""
from travel_agency.exceptions.travel_agency_exception import TravelAgencyException
from travel_agency.exceptions.invalid_client_data_exception import InvalidClientDataException
from travel_agency.exceptions.invalid_date_range_exception import InvalidDateRangeException
from travel_agency.exceptions.passport_expired_exception import PassportExpiredException
from travel_agency.exceptions.visa_required_exception import VisaRequiredException
from travel_agency.exceptions.room_not_available_exception import RoomNotAvailableException
from travel_agency.exceptions.seat_not_available_exception import SeatNotAvailableException
from travel_agency.exceptions.tour_fully_booked_exception import TourFullyBookedException
from travel_agency.exceptions.capacity_exceeded_exception import CapacityExceededException
from travel_agency.exceptions.booking_not_found_exception import BookingNotFoundException
from travel_agency.exceptions.invalid_booking_state_exception import InvalidBookingStateException
from travel_agency.exceptions.insufficient_funds_exception import InsufficientFundsException
from travel_agency.exceptions.card_expired_exception import CardExpiredException
from travel_agency.exceptions.invalid_payment_data_exception import InvalidPaymentDataException
from travel_agency.exceptions.invalid_promo_code_exception import InvalidPromoCodeException
from travel_agency.exceptions.refund_not_allowed_exception import RefundNotAllowedException
from travel_agency.exceptions.invalid_tour_data_exception import InvalidTourDataException
from travel_agency.exceptions.staff_not_qualified_exception import StaffNotQualifiedException
from travel_agency.exceptions.employee_not_found_exception import EmployeeNotFoundException
from travel_agency.exceptions.insurance_claim_rejected_exception import InsuranceClaimRejectedException

__all__ = [
    "TravelAgencyException",
    "InvalidClientDataException",
    "InvalidDateRangeException",
    "PassportExpiredException",
    "VisaRequiredException",
    "RoomNotAvailableException",
    "SeatNotAvailableException",
    "TourFullyBookedException",
    "CapacityExceededException",
    "BookingNotFoundException",
    "InvalidBookingStateException",
    "InsufficientFundsException",
    "CardExpiredException",
    "InvalidPaymentDataException",
    "InvalidPromoCodeException",
    "RefundNotAllowedException",
    "InvalidTourDataException",
    "StaffNotQualifiedException",
    "EmployeeNotFoundException",
    "InsuranceClaimRejectedException",
]
