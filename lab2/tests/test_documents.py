"""Тесты документов."""
import unittest
from datetime import date, datetime

from tests.factories import START, TODAY, make_city, make_client, make_country, make_flight, make_package, make_person
from travel_agency.booking.booking import Booking
from travel_agency.documents.identity import Passport, Visa
from travel_agency.documents.papers import Contract, InsurancePolicy, Voucher
from travel_agency.exceptions import (
    InsuranceClaimRejectedException,
    InvalidBookingStateException,
    InvalidDateRangeException,
    SeatNotAvailableException,
    VisaRequiredException,
)
from travel_agency.statuses import TicketStatus


class PassportVisaTest(unittest.TestCase):
    def test_passport(self):
        passport = Passport("MP1", make_country(), date(2020, 1, 1), date(2027, 1, 1))
        self.assertTrue(passport.is_valid_on(TODAY))
        self.assertFalse(passport.is_valid_on(date(2028, 1, 1)))
        self.assertTrue(passport.is_valid_for_trip(date(2026, 5, 1)))
        self.assertFalse(passport.is_valid_for_trip(date(2026, 12, 1)))
        with self.assertRaises(InvalidDateRangeException):
            Passport("MP2", make_country(), date(2027, 1, 1), date(2020, 1, 1))

    def test_visa_entries(self):
        country = make_country("Италия", "IT")
        visa = Visa("C", country, date(2026, 1, 1), date(2026, 6, 30), 1)
        self.assertTrue(visa.allows_stay_in(country, TODAY))
        self.assertFalse(visa.allows_stay_in(make_country(), TODAY))
        self.assertEqual(visa.register_entry(TODAY), 0)
        with self.assertRaises(VisaRequiredException):
            visa.register_entry(TODAY)
        with self.assertRaises(VisaRequiredException):
            visa.register_entry(date(2027, 1, 1))


class InsuranceTest(unittest.TestCase):
    def test_premium_and_claims(self):
        policy = InsurancePolicy("I1", make_person(), date(2026, 4, 1), date(2026, 4, 10), 10000.0)
        self.assertEqual(policy.calculate_premium(), 25.0)
        self.assertEqual(policy.file_claim(4000.0, date(2026, 4, 5)), 6000.0)
        with self.assertRaises(InsuranceClaimRejectedException):
            policy.file_claim(7000.0, date(2026, 4, 5))
        with self.assertRaises(InsuranceClaimRejectedException):
            policy.file_claim(10.0, date(2026, 5, 5))

    def test_senior_premium(self):
        senior = make_person()
        senior.birth_date = date(1950, 1, 1)
        policy = InsurancePolicy("I2", senior, date(2026, 4, 1), date(2026, 4, 10), 10000.0)
        self.assertEqual(policy.calculate_premium(), 37.5)


class ContractVoucherTest(unittest.TestCase):
    def setUp(self):
        client = make_client()
        self.booking = Booking("B1", client, make_package(client=client), TODAY)
        self.booking.calculate_total()
        self.contract = Contract("D1", client, self.booking, "Условия")

    def test_contract_lifecycle(self):
        with self.assertRaises(InvalidBookingStateException):
            self.contract.terminate(TODAY)
        self.contract.sign(TODAY)
        self.assertTrue(self.contract.is_signed)
        with self.assertRaises(InvalidBookingStateException):
            self.contract.sign(TODAY)
        penalty = self.contract.terminate(date(2026, 4, 5))
        self.assertEqual(penalty, self.booking.total_price)
        self.assertTrue(self.contract.is_terminated)

    def test_voucher(self):
        voucher = Voucher("V1", self.booking, TODAY)
        self.assertFalse(voucher.is_expired(date(2026, 3, 20)))
        voucher.redeem(TODAY)
        with self.assertRaises(InvalidBookingStateException):
            voucher.redeem(TODAY)
        self.assertTrue(Voucher("V2", self.booking, TODAY, 1).is_expired(START))


class TicketTest(unittest.TestCase):
    def setUp(self):
        self.flight = make_flight(make_city(), make_city("Анталья"))
        self.ticket = self.flight.issue_ticket(make_person())

    def test_check_in_window(self):
        with self.assertRaises(InvalidBookingStateException):
            self.ticket.check_in(datetime(2026, 4, 1, 9, 0))
        self.ticket.check_in(datetime(2026, 4, 9, 20, 0))
        self.assertIs(self.ticket.status, TicketStatus.CHECKED_IN)
        with self.assertRaises(InvalidBookingStateException):
            self.ticket.check_in(datetime(2026, 4, 9, 21, 0))

    def test_change_seat_and_cancel(self):
        self.ticket.change_seat("1F")
        self.assertEqual(self.ticket.price, 300.0)
        self.assertFalse(self.flight.seats["1A"].is_occupied)
        with self.assertRaises(SeatNotAvailableException):
            self.ticket.change_seat("1F")
        self.ticket.cancel()
        self.assertFalse(self.flight.seats["1F"].is_occupied)
        with self.assertRaises(InvalidBookingStateException):
            self.ticket.cancel()


if __name__ == "__main__":
    unittest.main()
