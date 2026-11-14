import unittest
from datetime import date
from tests.factories import START, make_city, make_client, make_hotel
from travel_agency.accommodation.hotel import Room, RoomType
from travel_agency.exceptions import (
    InvalidBookingStateException,
    InvalidDateRangeException,
    InvalidTourDataException,
    RoomNotAvailableException,
)


class HotelTest(unittest.TestCase):
    def setUp(self):
        self.hotel = make_hotel(make_city(), rooms=1, capacity=2)
        self.client = make_client()

    def test_rooms(self):
        lux = RoomType("Люкс", 2.0, True)
        self.hotel.add_room(Room("2", lux, 4, 50.0))
        self.assertEqual(self.hotel.rooms["2"].calculate_stay_cost(2), 200.0)
        self.assertEqual(self.hotel.find_available_room(3).number, "2")
        with self.assertRaises(InvalidTourDataException):
            self.hotel.add_room(Room("2", lux, 4, 50.0))
        with self.assertRaises(RoomNotAvailableException):
            self.hotel.find_available_room(5)

    def test_reservation(self):
        reservation = self.hotel.reserve_room(self.client, 2, START, date(2026, 4, 13))
        self.assertEqual(self.hotel.count_free_rooms(), 0)
        self.assertEqual(reservation.calculate_nights(), 3)
        self.assertEqual(reservation.calculate_total(), 150.0)
        reservation.choose_meal_plan("BB")
        self.assertEqual(reservation.calculate_total(), 210.0)
        with self.assertRaises(InvalidTourDataException):
            reservation.choose_meal_plan("AI")
        reservation.cancel()
        self.assertEqual(self.hotel.count_free_rooms(), 1)
        with self.assertRaises(InvalidBookingStateException):
            reservation.cancel()

    def test_reservation_dates(self):
        with self.assertRaises(InvalidDateRangeException):
            self.hotel.reserve_room(self.client, 1, START, date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
