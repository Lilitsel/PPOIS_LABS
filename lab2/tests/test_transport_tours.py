"""Тесты транспорта, туров и ценообразования."""
import unittest
from datetime import date, datetime, timedelta

from tests.factories import START, TODAY, make_city, make_client, make_flight, make_package, make_person, make_tour
from travel_agency.documents.papers import InsurancePolicy
from travel_agency.exceptions import (
    CapacityExceededException,
    InvalidBookingStateException,
    InvalidPromoCodeException,
    InvalidTourDataException,
    SeatNotAvailableException,
    StaffNotQualifiedException,
    TourFullyBookedException,
)
from travel_agency.geography.places import Address, Attraction
from travel_agency.people.staff import Driver, Guide
from travel_agency.service.clients import Review
from travel_agency.tours.pricing import Discount, PromoCode, TourPackage
from travel_agency.tours.tour import Excursion, GroupTour, Itinerary, ItineraryDay, Season
from travel_agency.transport.air import Seat
from travel_agency.transport.ground import Bus, Transfer


class FlightTest(unittest.TestCase):
    def setUp(self):
        self.origin, self.target = make_city(), make_city("Анталья")
        self.flight = make_flight(self.origin, self.target, seats=1)

    def test_flight_basics(self):
        self.assertEqual(self.flight.calculate_duration(), timedelta(hours=3))
        self.assertTrue(self.flight.flies_to(self.target))
        self.assertTrue(self.flight.arrival_airport.has_terminal("2"))
        self.assertEqual(self.flight.airline.calculate_baggage_fee(23), 15.0)
        self.assertEqual(self.flight.airline.calculate_baggage_fee(10), 0.0)
        with self.assertRaises(InvalidTourDataException):
            self.flight.add_seat(Seat("1A", "economy", 1.0))

    def test_seats(self):
        ticket = self.flight.issue_ticket(make_person(), "economy")
        self.assertEqual(ticket.price, 150.0)
        with self.assertRaises(SeatNotAvailableException):
            self.flight.find_free_seat("economy")
        with self.assertRaises(SeatNotAvailableException):
            self.flight.book_seat("99Z")
        with self.assertRaises(SeatNotAvailableException):
            self.flight.book_seat("1A")
        self.assertEqual(self.flight.find_free_seat().number, "1F")


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


class PricingTest(unittest.TestCase):
    def setUp(self):
        self.discount = Discount("Весна", 10, date(2026, 12, 31), 100.0)

    def test_discount(self):
        self.assertEqual(self.discount.apply(1000.0, TODAY), 1000.0)
        self.discount.is_approved = True
        self.assertEqual(self.discount.apply(1000.0, TODAY), 900.0)
        self.assertEqual(self.discount.apply(50.0, TODAY), 50.0)
        with self.assertRaises(InvalidPromoCodeException):
            Discount("Ошибка", 150, TODAY)

    def test_promo_code(self):
        self.discount.is_approved = True
        promo = PromoCode("spring", self.discount, 1)
        self.assertEqual(promo.redeem(1000.0, TODAY), 900.0)
        self.assertTrue(promo.is_exhausted())
        with self.assertRaises(InvalidPromoCodeException):
            promo.redeem(1000.0, TODAY)

    def test_package_price(self):
        client = make_client()
        package = make_package(client=client)
        package.flight = make_flight(make_city(), package.tour.destination.city)
        bus = Bus("1", 10, "D", True)
        package.transfer = Transfer((None, None), datetime(2026, 4, 10, 12, 0), bus, 10.0)
        package.insurances.append(InsurancePolicy("I", client, START, package.end_date, 1000.0))
        self.assertEqual(package.calculate_total_price(TODAY), 400 + 350 + 150 + 18 + 13)
        self.discount.is_approved = True
        package.apply_discount(self.discount)
        self.assertEqual(package.calculate_total_price(TODAY), 837.9)
        self.assertGreater(package.calculate_total_price(), 0)

    def test_package_validation(self):
        package = TourPackage(make_tour(), START, 2)
        with self.assertRaises(InvalidTourDataException):
            package.validate_completeness()
        package = make_package(travelers=1)
        package.travelers_count = 2
        with self.assertRaises(InvalidTourDataException):
            package.validate_completeness()
        with self.assertRaises(InvalidTourDataException):
            TourPackage(make_tour(), START, 0)
        TourPackage(make_tour(duration=1), START, 1).validate_completeness()


if __name__ == "__main__":
    unittest.main()
