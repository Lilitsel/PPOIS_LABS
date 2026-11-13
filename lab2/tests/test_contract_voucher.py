import unittest
from datetime import date
from tests.factories import START, TODAY, make_client, make_package
from travel_agency.booking.booking import Booking
from travel_agency.documents.papers import Contract, Voucher
from travel_agency.exceptions import InvalidBookingStateException


class ContractVoucherTest(unittest.TestCase):
    def setUp(self):
        client = make_client()
        self.booking = Booking("B1", client, make_package(client=client), TODAY)
        self.booking.calculate_total()
        self.contract = Contract("D1", client, self.booking, "Условия")

    def test_contract_lifecycle(self):
        with self.assertRaises(InvalidBookingStateException):
            self.contract.terminate(TODAY)
        self.contract.sign(TODAY)
        self.assertTrue(self.contract.is_signed)
        with self.assertRaises(InvalidBookingStateException):
            self.contract.sign(TODAY)
        penalty = self.contract.terminate(date(2026, 4, 5))
        self.assertEqual(penalty, self.booking.total_price)
        self.assertTrue(self.contract.is_terminated)

    def test_voucher(self):
        voucher = Voucher("V1", self.booking, TODAY)
        self.assertFalse(voucher.is_expired(date(2026, 3, 20)))
        voucher.redeem(TODAY)
        with self.assertRaises(InvalidBookingStateException):
            voucher.redeem(TODAY)
        self.assertTrue(Voucher("V2", self.booking, TODAY, 1).is_expired(START))


if __name__ == "__main__":
    unittest.main()
