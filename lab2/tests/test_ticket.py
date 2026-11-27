import unittest
from datetime import datetime
from tests.factories import make_city, make_flight, make_person
from travel_agency.exceptions import InvalidBookingStateException, SeatNotAvailableException
from travel_agency.statuses import TicketStatus


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
