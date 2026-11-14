import unittest
from tests.factories import TODAY, make_client, make_package, make_tour
from travel_agency.booking.booking import Booking
from travel_agency.exceptions import InvalidBookingStateException, InvalidClientDataException
from travel_agency.service.clients import Complaint, Review


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


if __name__ == "__main__":
    unittest.main()
