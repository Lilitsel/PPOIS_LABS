import unittest
from datetime import date
from tests.factories import TODAY, make_client, make_package
from travel_agency.booking.booking import Booking
from travel_agency.service.notifications import NotificationService


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


if __name__ == "__main__":
    unittest.main()
