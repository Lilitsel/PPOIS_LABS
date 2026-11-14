import unittest
from datetime import date
from tests.factories import TODAY, make_client, make_country, make_package
from travel_agency.booking.booking import Booking
from travel_agency.documents.identity import Passport, Visa
from travel_agency.exceptions import InvalidClientDataException, PassportExpiredException, VisaRequiredException
from travel_agency.geography.places import Country
from travel_agency.people.person import Client


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.home = make_country()
        self.italy = Country("Италия", "IT", "EUR")
        self.client = make_client(home=self.home)
        self.return_date = date(2026, 5, 1)

    def test_bookings(self):
        booking = Booking("B1", self.client, make_package(client=self.client), TODAY)
        self.client.add_booking(booking)
        self.client.add_booking(booking)
        self.assertEqual(self.client.get_active_bookings(), [booking])

    def test_no_passport(self):
        client = Client("C9", "A", "B", date(2000, 1, 1), "1", "a@b")
        with self.assertRaises(InvalidClientDataException):
            client.check_travel_documents(self.italy, self.return_date)

    def test_expiring_passport(self):
        self.client.passport = Passport("P", self.home, date(2020, 1, 1), date(2026, 6, 1))
        with self.assertRaises(PassportExpiredException):
            self.client.check_travel_documents(self.italy, self.return_date)
        self.assertFalse(self.client.can_travel_to(self.italy, self.return_date))

    def test_visa_rules(self):
        with self.assertRaises(VisaRequiredException):
            self.client.check_travel_documents(self.italy, self.return_date)
        self.client.add_visa(Visa("C", self.italy, date(2026, 1, 1), date(2026, 12, 31), 1))
        self.assertTrue(self.client.can_travel_to(self.italy, self.return_date))
        self.assertTrue(self.client.can_travel_to(self.home, self.return_date))


if __name__ == "__main__":
    unittest.main()
