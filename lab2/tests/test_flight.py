import unittest
from datetime import timedelta
from tests.factories import make_city, make_flight, make_person
from travel_agency.exceptions import InvalidTourDataException, SeatNotAvailableException
from travel_agency.transport.air import Seat


class FlightTest(unittest.TestCase):
    def setUp(self):
        self.origin, self.target = make_city(), make_city("Анталья")
        self.flight = make_flight(self.origin, self.target, seats=1)

    def test_flight_basics(self):
        self.assertEqual(self.flight.calculate_duration(), timedelta(hours=3))
        self.assertTrue(self.flight.flies_to(self.target))
        self.assertTrue(self.flight.arrival_airport.has_terminal("2"))
        self.assertEqual(self.flight.airline.calculate_baggage_fee(23), 15.0)
        self.assertEqual(self.flight.airline.calculate_baggage_fee(10), 0.0)
        with self.assertRaises(InvalidTourDataException):
            self.flight.add_seat(Seat("1A", "economy", 1.0))

    def test_seats(self):
        ticket = self.flight.issue_ticket(make_person(), "economy")
        self.assertEqual(ticket.price, 150.0)
        with self.assertRaises(SeatNotAvailableException):
            self.flight.find_free_seat("economy")
        with self.assertRaises(SeatNotAvailableException):
            self.flight.book_seat("99Z")
        with self.assertRaises(SeatNotAvailableException):
            self.flight.book_seat("1A")
        self.assertEqual(self.flight.find_free_seat().number, "1F")


if __name__ == "__main__":
    unittest.main()
