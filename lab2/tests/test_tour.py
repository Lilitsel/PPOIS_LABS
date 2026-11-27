import unittest
from datetime import date
from tests.factories import START, TODAY, make_client, make_person, make_tour
from travel_agency.exceptions import InvalidTourDataException, TourFullyBookedException
from travel_agency.people.staff import Guide
from travel_agency.service.clients import Review
from travel_agency.tours.tour import GroupTour, Season


class TourTest(unittest.TestCase):
    def setUp(self):
        self.tour = make_tour(max_group=3)
        self.city = self.tour.destination.city

    def test_seasons(self):
        summer, winter = Season("Лето", 6, 8, 1.5), Season("Зима", 12, 2, 0.8)
        self.tour.add_season(summer)
        self.tour.add_season(winter)
        self.assertTrue(winter.contains_date(date(2026, 1, 5)))
        self.assertFalse(winter.contains_date(date(2026, 5, 5)))
        self.assertEqual(summer.adjust_price(100), 150)
        self.assertEqual(self.tour.calculate_price_for_group(2, date(2026, 7, 1)), 1200.0)
        self.assertEqual(self.tour.calculate_price_for_group(1, START), 400.0)
        self.assertFalse(self.tour.is_available_in_season(START))
        with self.assertRaises(InvalidTourDataException):
            Season("Плохой", 0, 13, 1.0)

    def test_places(self):
        self.tour.reserve_places(3)
        self.assertFalse(self.tour.has_free_places())
        with self.assertRaises(TourFullyBookedException):
            self.tour.reserve_places(1)
        self.tour.release_places(5)
        self.assertEqual(self.tour.free_places(), 3)
        with self.assertRaises(InvalidTourDataException):
            make_tour(duration=0)

    def test_reviews(self):
        self.assertEqual(self.tour.average_rating(), 0.0)
        self.tour.add_review(Review(make_client(), self.tour, 5, "Отлично", TODAY))
        self.tour.add_review(Review(make_client(), self.tour, 3, "Нормально", TODAY))
        self.assertEqual(self.tour.average_rating(), 4.0)
        self.assertEqual(self.tour.destination_name, "Анталья")

    def test_group_tour(self):
        guide = Guide("G1", make_person(), 1.0, TODAY, {"ru"})
        group = GroupTour(self.tour, guide, 2)
        self.assertFalse(group.is_confirmed())
        group.reserve_places(2)
        self.assertTrue(group.is_confirmed())
        self.assertEqual(group.calculate_price_for_group(1, START), 360.0)
        with self.assertRaises(InvalidTourDataException):
            GroupTour(self.tour, guide, 10)


if __name__ == "__main__":
    unittest.main()
