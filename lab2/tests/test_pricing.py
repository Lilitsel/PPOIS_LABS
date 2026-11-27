import unittest
from datetime import date, datetime
from tests.factories import START, TODAY, make_city, make_client, make_flight, make_package, make_tour
from travel_agency.documents.papers import InsurancePolicy
from travel_agency.exceptions import InvalidPromoCodeException, InvalidTourDataException
from travel_agency.tours.pricing import Discount, PromoCode, TourPackage
from travel_agency.transport.ground import Bus, Transfer


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
