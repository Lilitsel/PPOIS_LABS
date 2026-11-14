import unittest
from datetime import datetime
from tests.factories import TODAY, make_city, make_client, make_person
from travel_agency.exceptions import CapacityExceededException, InvalidBookingStateException
from travel_agency.geography.places import Address
from travel_agency.people.staff import Driver
from travel_agency.transport.ground import Bus, Transfer


class TransferTest(unittest.TestCase):
    def setUp(self):
        city = make_city()
        route = (Address("Аэропорт", "1", "1", city), Address("Отель", "2", "2", city))
        self.bus = Bus("1234", 1, "d", True)
        self.transfer = Transfer(route, datetime(2026, 4, 10, 12, 0), self.bus, 60.0)

    def test_transfer(self):
        self.transfer.add_passenger(make_client())
        with self.assertRaises(CapacityExceededException):
            self.transfer.add_passenger(make_client("C2"))
        self.assertEqual(self.transfer.calculate_cost(), 58.0)
        self.assertEqual(self.transfer.estimate_arrival(), datetime(2026, 4, 10, 13, 0))
        with self.assertRaises(InvalidBookingStateException):
            self.transfer.complete()

    def test_complete(self):
        Driver("D1", make_person(), 1.0, TODAY, {"D"}).assign_transfer(self.transfer)
        self.transfer.complete()
        self.assertEqual(self.bus.mileage_km, 60.0)
        self.assertTrue(self.transfer.is_completed)


if __name__ == "__main__":
    unittest.main()
