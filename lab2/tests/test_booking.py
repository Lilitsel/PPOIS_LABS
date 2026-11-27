import unittest
from datetime import date
from tests.factories import TODAY, make_client, make_package, make_person
from travel_agency.booking.booking import Booking
from travel_agency.exceptions import CapacityExceededException, InvalidBookingStateException
from travel_agency.statuses import BookingStatus


class BookingTest(unittest.TestCase):
    def setUp(self):
        self.client = make_client()
        self.booking = Booking("B1", self.client, make_package(client=self.client, travelers=2), TODAY)

    def test_travelers_and_confirm(self):
        self.booking.add_traveler(make_person())
        with self.assertRaises(CapacityExceededException):
            self.booking.add_traveler(make_person())
        self.booking.confirm()
        self.assertEqual(self.booking.package.tour.booked_places, 2)
        with self.assertRaises(InvalidBookingStateException):
            self.booking.confirm()
        self.booking.complete()
        self.assertIs(self.booking.status, BookingStatus.COMPLETED)
        self.assertFalse(self.booking.is_active())

    def test_cancel_confirmed(self):
        self.booking.calculate_total()
        self.booking.confirm()
        cancellation = self.booking.cancel("болезнь", date(2026, 4, 1))
        self.assertEqual(self.booking.package.tour.booked_places, 0)
        self.assertEqual(cancellation.days_before_departure(), 9)
        self.assertEqual(cancellation.penalty_amount, self.booking.total_price / 2)
        self.assertEqual(cancellation.calculate_refund_amount(self.booking.total_price), self.booking.total_price / 2)
        with self.assertRaises(InvalidBookingStateException):
            self.booking.cancel("ещё раз", TODAY)

    def test_cancel_pending_without_hotel(self):
        self.booking.package.hotel_reservation = None
        self.booking.cancel("передумал", TODAY)
        self.assertIs(self.booking.status, BookingStatus.CANCELLED)
        self.assertEqual(self.booking.destination_name(), "Анталья")


if __name__ == "__main__":
    unittest.main()
