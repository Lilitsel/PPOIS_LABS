import unittest
from datetime import date
from tests.factories import make_person
from travel_agency.exceptions import InvalidClientDataException
from travel_agency.people.person import Person


class PersonTest(unittest.TestCase):
    def test_age_before_and_after_birthday(self):
        person = make_person()
        self.assertEqual(person.calculate_age(date(2026, 6, 14)), 35)
        self.assertEqual(person.calculate_age(date(2026, 6, 15)), 36)
        self.assertTrue(person.is_adult(date(2026, 1, 1)))
        self.assertGreater(person.calculate_age(), 0)
        self.assertEqual(person.full_name, "Иван Петров")

    def test_invalid_data(self):
        with self.assertRaises(InvalidClientDataException):
            Person(" ", "X", date(2000, 1, 1), "1", "a@b")
        with self.assertRaises(InvalidClientDataException):
            Person("A", "B", date(2000, 1, 1), "1", "no-at-sign")


if __name__ == "__main__":
    unittest.main()
