import unittest
from datetime import date, datetime
from tests.factories import make_city, make_country
from travel_agency.documents.identity import Passport
from travel_agency.exceptions import InvalidTourDataException
from travel_agency.geography.places import Address, Attraction, Destination


class GeographyTest(unittest.TestCase):
    def test_country_visa_rules(self):
        home, turkey = make_country(), make_country("Турция", "TR")
        passport = Passport("P", home, date(2020, 1, 1), date(2030, 1, 1))
        self.assertTrue(turkey.requires_visa_for(passport))
        turkey.add_visa_free_country("by")
        self.assertFalse(turkey.requires_visa_for(passport))
        self.assertFalse(home.requires_visa_for(passport))
        self.assertTrue(turkey.is_safe_for_travel())
        turkey.safety_level = 4
        self.assertFalse(turkey.is_safe_for_travel())

    def test_city(self):
        minsk = make_city()
        moscow = make_city("Москва", lat=55.75, lon=37.62)
        self.assertAlmostEqual(minsk.distance_to(moscow), 675, delta=10)
        self.assertEqual(minsk.local_time(datetime(2026, 1, 1, 10)).hour, 13)
        self.assertIn("Минск", Address("Ленина", "5", "220000", minsk).format_full())

    def test_attraction(self):
        museum = Attraction("Музей", make_city(), "история", 10.0, 9, 18)
        self.assertTrue(museum.is_open_at(9))
        self.assertFalse(museum.is_open_at(18))
        self.assertEqual(museum.calculate_group_fee(2), 20.0)
        self.assertEqual(museum.calculate_group_fee(10), 85.0)

    def test_destination(self):
        city = make_city()
        destination = Destination(city, "умеренный", {6, 7})
        self.assertTrue(destination.is_recommended_in_month(6))
        destination.add_attraction(Attraction("Музей", city, "история", 1.0, 9, 18))
        self.assertEqual(len(destination.find_attractions_by_category("история")), 1)
        self.assertIs(destination.country, city.country)
        with self.assertRaises(InvalidTourDataException):
            destination.add_attraction(Attraction("Чужой", make_city("Рим"), "история", 1.0, 9, 18))
        with self.assertRaises(InvalidTourDataException):
            Destination(city, "x", {13})


if __name__ == "__main__":
    unittest.main()
