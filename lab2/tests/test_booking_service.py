import unittest
from datetime import date
from tests.factories import TODAY, make_client, make_country, make_package, make_service, make_tour
from travel_agency.exceptions import (
    BookingNotFoundException,
    InvalidBookingStateException,
    TourFullyBookedException,
    VisaRequiredException,
)
from travel_agency.service.clients import LoyaltyCard
from travel_agency.statuses import BookingStatus, PaymentStatus


def make_loyal_client():
    client = make_client()
    client.loyalty_card = LoyaltyCard("L1")
    return client


class BookingServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = make_service()
        self.client = make_loyal_client()
        self.package = make_package(client=self.client)
        self.package.destination_country().add_visa_free_country("BY")

    def test_full_flow(self):
        booking = self.service.create_booking(self.client, self.package, TODAY)
        self.assertEqual(self.service.find_by_client(self.client), [booking])
        payment = self.service.pay_booking(booking.booking_id, self.client.bank_card, TODAY)
        self.assertIs(booking.status, BookingStatus.CONFIRMED)
        self.assertGreater(self.client.loyalty_card.points, 0)
        with self.assertRaises(InvalidBookingStateException):
            self.service.pay_booking(booking.booking_id, self.client.bank_card, TODAY)
        balance_before = self.client.bank_card.balance
        self.service.cancel_booking(booking.booking_id, "болезнь", date(2026, 3, 20))
        self.assertIs(payment.status, PaymentStatus.REFUNDED)
        self.assertEqual(self.client.bank_card.balance, balance_before + payment.amount * 0.75)
        self.assertEqual(len(self.service.notifier.history_for(self.client)), 2)

    def test_errors(self):
        with self.assertRaises(BookingNotFoundException):
            self.service.find_booking("NOPE")
        italy_tour = make_tour(city=None)
        italy_tour.destination.city.country = make_country("Италия", "IT")
        with self.assertRaises(VisaRequiredException):
            self.service.create_booking(self.client, make_package(tour=italy_tour, client=self.client), TODAY)
        self.package.tour.reserve_places(self.package.tour.max_group_size)
        with self.assertRaises(InvalidBookingStateException):
            self.service.create_booking(self.client, self.package, TODAY)

    def test_rollback_when_tour_filled(self):
        booking = self.service.create_booking(self.client, self.package, TODAY)
        self.package.tour.reserve_places(self.package.tour.max_group_size)
        balance = self.client.bank_card.balance
        with self.assertRaises(TourFullyBookedException):
            self.service.pay_booking(booking.booking_id, self.client.bank_card, TODAY)
        self.assertEqual(self.client.bank_card.balance, balance)

    def test_cancel_unpaid_without_loyalty(self):
        self.client.loyalty_card = None
        booking = self.service.create_booking(self.client, self.package, TODAY)
        cancellation = self.service.cancel_booking(booking.booking_id, "x", TODAY)
        self.assertEqual(cancellation.booking, booking)
        self.assertIsNone(self.service._reward_loyalty(self.client, 100.0))


if __name__ == "__main__":
    unittest.main()
