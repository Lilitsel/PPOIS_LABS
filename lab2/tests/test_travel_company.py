import unittest
from datetime import date, datetime
from tests.factories import START, TODAY, make_city, make_client, make_flight, make_hotel, make_service, make_tour
from travel_agency.company.company import Branch, TravelCompany
from travel_agency.exceptions import (
    InvalidClientDataException,
    InvalidTourDataException,
    RoomNotAvailableException,
    VisaRequiredException,
)
from travel_agency.geography.places import Address


class TravelCompanyTest(unittest.TestCase):
    def setUp(self):
        self.home_city = make_city()
        self.company = TravelCompany("Тест", "LIC", make_service(), self.home_city.country)
        self.tour = make_tour()
        self.city = self.tour.destination.city
        self.company.add_tour(self.tour)
        self.company.add_partner_hotel(make_hotel(self.city, rooms=1))
        self.company.add_flight(make_flight(self.home_city, self.city, datetime(2026, 4, 10, 9, 0)))
        self.client = make_client(home=self.home_city.country)
        self.company.register_client(self.client)
        self.company.open_branch(Branch("Офис", Address("A", "1", "1", self.home_city), 9, 18))

    def test_registry(self):
        with self.assertRaises(InvalidClientDataException):
            self.company.register_client(self.client)
        with self.assertRaises(InvalidClientDataException):
            self.company.find_client("X")
        with self.assertRaises(InvalidTourDataException):
            self.company.add_tour(self.tour)
        with self.assertRaises(InvalidTourDataException):
            self.company.find_tour("X")
        self.assertEqual(len(self.company.branches), 1)

    def test_search(self):
        self.assertEqual(self.company.search_tours(), [self.tour])
        self.assertEqual(self.company.search_tours(max_price=100.0), [])
        self.assertEqual(self.company.search_tours(month=5), [self.tour])
        self.assertEqual(self.company.search_tours(month=1), [])

    def test_assemble_and_book(self):
        self.city.country.add_visa_free_country("BY")
        booking = self.company.book_tour("C1", "T1", (START, 1), TODAY)
        self.assertIsNotNone(booking.package.flight)
        self.assertEqual(self.company.all_bookings(), [booking])
        self.assertIsNone(self.company.find_flight_to(self.city, date(2026, 5, 1)))
        with self.assertRaises(RoomNotAvailableException):
            self.company.book_tour("C1", "T1", (START, 1), TODAY)
        with self.assertRaises(RoomNotAvailableException):
            self.company.find_hotel_in_city(self.home_city)

    def test_failed_booking_releases_room(self):
        with self.assertRaises(VisaRequiredException):
            self.company.book_tour("C1", "T1", (START, 1), TODAY)
        hotel = self.company.find_hotel_in_city(self.city)
        self.assertEqual(hotel.count_free_rooms(), 1)


if __name__ == "__main__":
    unittest.main()
