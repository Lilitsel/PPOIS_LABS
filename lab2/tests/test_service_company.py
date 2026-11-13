"""Тесты клиентского сервиса и компании."""
import unittest
from datetime import date, datetime

from tests.factories import (
    START,
    TODAY,
    make_city,
    make_client,
    make_flight,
    make_hotel,
    make_package,
    make_person,
    make_service,
    make_tour,
)
from travel_agency.booking.booking import Booking
from travel_agency.company.company import Branch, TravelCompany
from travel_agency.exceptions import (
    EmployeeNotFoundException,
    InsufficientFundsException,
    InvalidBookingStateException,
    InvalidClientDataException,
    InvalidTourDataException,
    RoomNotAvailableException,
    VisaRequiredException,
)
from travel_agency.geography.places import Address
from travel_agency.people.staff import Employee
from travel_agency.service.clients import Complaint, LoyaltyCard, Review
from travel_agency.service.notifications import NotificationService


class LoyaltyTest(unittest.TestCase):
    def test_points_and_tiers(self):
        card = LoyaltyCard("L1")
        self.assertEqual(card.add_points(1000.0), 100)
        self.assertEqual(card.tier, "BASIC")
        card.add_points(10000.0)
        self.assertEqual(card.tier, "SILVER")
        self.assertEqual(card.add_points(1000.0), 120)
        self.assertEqual(card.redeem_points(100), 50.0)
        with self.assertRaises(InsufficientFundsException):
            card.redeem_points(10 ** 6)
        with self.assertRaises(InsufficientFundsException):
            card.redeem_points(0)


class ReviewComplaintTest(unittest.TestCase):
    def setUp(self):
        self.client = make_client()
        self.tour = make_tour()

    def test_review(self):
        self.assertTrue(Review(self.client, self.tour, 5, "Супер", TODAY).is_positive())
        self.assertFalse(Review(self.client, self.tour, 2, "Так себе", TODAY).is_positive())
        with self.assertRaises(InvalidClientDataException):
            Review(self.client, self.tour, 0, "x", TODAY)
        with self.assertRaises(InvalidClientDataException):
            Review(self.client, self.tour, 5, "Тут РЕКЛАМА", TODAY)

    def test_complaint(self):
        booking = Booking("B1", self.client, make_package(client=self.client), TODAY)
        complaint = Complaint(self.client, booking, "Нет горячей воды")
        for expected_level in (1, 2, 3):
            self.assertEqual(complaint.escalate(), expected_level)
        with self.assertRaises(InvalidBookingStateException):
            complaint.escalate()
        complaint.resolve("Компенсация")
        with self.assertRaises(InvalidBookingStateException):
            complaint.resolve("ещё")
        with self.assertRaises(InvalidBookingStateException):
            complaint.escalate()


class NotificationTest(unittest.TestCase):
    def test_notifications(self):
        service = NotificationService("sms")
        client, other = make_client(), make_client("C2")
        booking = Booking("B1", client, make_package(client=client), TODAY)
        self.assertIsNone(service.notify_departure_reminder(booking, TODAY))
        reminder = service.notify_departure_reminder(booking, date(2026, 4, 8))
        self.assertTrue(reminder.is_sent())
        self.assertIn("2", reminder.message)
        self.assertEqual(service.send_bulk([client, other], "Акция"), 2)
        self.assertEqual(len(service.history_for(client)), 2)
        self.assertEqual(reminder.channel, "sms")


class BranchTest(unittest.TestCase):
    def test_staff(self):
        branch = Branch("Офис", Address("Ленина", "1", "1", make_city()), 9, 18)
        employee = Employee("E1", make_person(), "Кассир", 1000.0, TODAY)
        branch.hire_employee(employee)
        self.assertIs(employee.branch, branch)
        with self.assertRaises(InvalidClientDataException):
            branch.hire_employee(employee)
        self.assertEqual(branch.calculate_payroll(), 1000.0)
        self.assertTrue(branch.is_open_at(10))
        self.assertIs(branch.fire_employee("E1"), employee)
        self.assertIsNone(employee.branch)
        with self.assertRaises(EmployeeNotFoundException):
            branch.fire_employee("E1")


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
