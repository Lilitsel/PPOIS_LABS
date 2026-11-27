import unittest
from datetime import date
from tests.factories import TODAY, make_country
from travel_agency.documents.identity import Passport, Visa
from travel_agency.exceptions import InvalidDateRangeException, VisaRequiredException


class PassportVisaTest(unittest.TestCase):
    def test_passport(self):
        passport = Passport("MP1", make_country(), date(2020, 1, 1), date(2027, 1, 1))
        self.assertTrue(passport.is_valid_on(TODAY))
        self.assertFalse(passport.is_valid_on(date(2028, 1, 1)))
        self.assertTrue(passport.is_valid_for_trip(date(2026, 5, 1)))
        self.assertFalse(passport.is_valid_for_trip(date(2026, 12, 1)))
        with self.assertRaises(InvalidDateRangeException):
            Passport("MP2", make_country(), date(2027, 1, 1), date(2020, 1, 1))

    def test_visa_entries(self):
        country = make_country("Италия", "IT")
        visa = Visa("C", country, date(2026, 1, 1), date(2026, 6, 30), 1)
        self.assertTrue(visa.allows_stay_in(country, TODAY))
        self.assertFalse(visa.allows_stay_in(make_country(), TODAY))
        self.assertEqual(visa.register_entry(TODAY), 0)
        with self.assertRaises(VisaRequiredException):
            visa.register_entry(TODAY)
        with self.assertRaises(VisaRequiredException):
            visa.register_entry(date(2027, 1, 1))


if __name__ == "__main__":
    unittest.main()
