import unittest
from travel_agency.exceptions import InsufficientFundsException
from travel_agency.service.clients import LoyaltyCard


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


if __name__ == "__main__":
    unittest.main()
