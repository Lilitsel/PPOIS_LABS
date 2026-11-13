import unittest
from datetime import date
from tests.factories import make_person
from travel_agency.documents.papers import InsurancePolicy
from travel_agency.exceptions import InsuranceClaimRejectedException


class InsuranceTest(unittest.TestCase):
    def test_premium_and_claims(self):
        policy = InsurancePolicy("I1", make_person(), date(2026, 4, 1), date(2026, 4, 10), 10000.0)
        self.assertEqual(policy.calculate_premium(), 25.0)
        self.assertEqual(policy.file_claim(4000.0, date(2026, 4, 5)), 6000.0)
        with self.assertRaises(InsuranceClaimRejectedException):
            policy.file_claim(7000.0, date(2026, 4, 5))
        with self.assertRaises(InsuranceClaimRejectedException):
            policy.file_claim(10.0, date(2026, 5, 5))

    def test_senior_premium(self):
        senior = make_person()
        senior.birth_date = date(1950, 1, 1)
        policy = InsurancePolicy("I2", senior, date(2026, 4, 1), date(2026, 4, 10), 10000.0)
        self.assertEqual(policy.calculate_premium(), 37.5)


if __name__ == "__main__":
    unittest.main()
