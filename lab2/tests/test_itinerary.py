import unittest
from tests.factories import TODAY, make_city, make_client, make_person
from travel_agency.exceptions import CapacityExceededException, InvalidTourDataException, StaffNotQualifiedException
from travel_agency.geography.places import Attraction
from travel_agency.people.staff import Guide
from travel_agency.tours.tour import Excursion, Itinerary, ItineraryDay


class ItineraryTest(unittest.TestCase):
    def setUp(self):
        self.minsk, self.moscow = make_city(), make_city("Москва", lat=55.75, lon=37.62)
        self.attraction = Attraction("Музей", self.minsk, "история", 5.0, 9, 18)

    def test_excursion(self):
        excursion = Excursion("Обзорная", self.attraction, "ru", 2, 20.0, 1)
        client = make_client()
        excursion.register_participant(client)
        excursion.register_participant(client)
        self.assertTrue(excursion.is_full())
        with self.assertRaises(CapacityExceededException):
            excursion.register_participant(make_client("C2"))
        self.assertEqual(excursion.calculate_revenue(), 15.0)
        with self.assertRaises(StaffNotQualifiedException):
            Guide("G", make_person(), 1, TODAY, {"en"}).assign_to_excursion(excursion)

    def test_days(self):
        itinerary = Itinerary()
        with self.assertRaises(InvalidTourDataException):
            itinerary.remove_last_day()
        day_one = ItineraryDay(1, self.minsk, 4)
        day_one.add_excursion(Excursion("Обзорная", self.attraction, "ru", 6, 20.0, 5))
        with self.assertRaises(InvalidTourDataException):
            day_one.add_excursion(Excursion("Длинная", self.attraction, "ru", 6, 20.0, 5))
        itinerary.add_day(day_one)
        itinerary.add_day(ItineraryDay(2, self.moscow, 8))
        with self.assertRaises(InvalidTourDataException):
            itinerary.add_day(ItineraryDay(5, self.moscow, 8))
        self.assertGreater(itinerary.total_distance_km, 600)
        self.assertEqual(itinerary.count_activities(), 1)
        self.assertEqual(itinerary.remove_last_day().day_number, 2)
        self.assertAlmostEqual(itinerary.total_distance_km, 0.0)
        itinerary.remove_last_day()


if __name__ == "__main__":
    unittest.main()
