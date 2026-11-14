import unittest
from datetime import date, datetime
from tests.factories import TODAY, make_card, make_city, make_client, make_package, make_person
from travel_agency.booking.booking import Booking
from travel_agency.exceptions import (
    InvalidBookingStateException,
    InvalidClientDataException,
    RefundNotAllowedException,
    StaffNotQualifiedException,
)
from travel_agency.finance.cards import PaymentProcessor, Refund
from travel_agency.geography.places import Address, Attraction
from travel_agency.people.staff import Accountant, Driver, Employee, Guide, Manager, TravelAgent
from travel_agency.service.clients import Complaint
from travel_agency.statuses import ComplaintStatus, RefundStatus
from travel_agency.tours.pricing import Discount
from travel_agency.tours.tour import Excursion
from travel_agency.transport.ground import Bus, Transfer


class StaffTest(unittest.TestCase):
    def setUp(self):
        self.person = make_person()

    def test_employee_bonus(self):
        employee = Employee("E1", self.person, "Кассир", 1000.0, date(2020, 1, 1))
        self.assertEqual(employee.calculate_experience_years(date(2025, 1, 2)), 5)
        self.assertEqual(employee.calculate_bonus(date(2025, 1, 2)), 100.0)
        self.assertEqual(employee.calculate_bonus(date(2040, 1, 2)), 200.0)
        self.assertGreaterEqual(employee.calculate_experience_years(), 0)

    def test_travel_agent_commission(self):
        agent = TravelAgent("A1", self.person, 900.0, date(2024, 1, 1))
        client = make_client()
        booking = Booking("B1", client, make_package(client=client), TODAY)
        booking.calculate_total()
        agent.sell_tour(booking)
        agent.assign_client(client)
        self.assertEqual(agent.assigned_clients, [client])
        self.assertAlmostEqual(agent.calculate_commission(), booking.total_price * 0.05)

    def test_guide(self):
        guide = Guide("G1", self.person, 800.0, date(2024, 1, 1), {"English", "Русский"})
        attraction = Attraction("Музей", make_city(), "история", 5.0, 9, 18)
        excursion = Excursion("Обзорная", attraction, "english", 2, 20.0, 10)
        guide.assign_to_excursion(excursion)
        self.assertIs(excursion.guide, guide)
        with self.assertRaises(StaffNotQualifiedException):
            guide.assign_to_excursion(Excursion("X", attraction, "Deutsch", 1, 10.0, 5))
        self.assertEqual(guide.update_rating(5), 5.0)
        self.assertEqual(guide.update_rating(3), 4.0)
        with self.assertRaises(InvalidClientDataException):
            guide.update_rating(6)

    def test_manager(self):
        manager = Manager("M1", self.person, 1500.0, date(2020, 1, 1), approval_limit=100.0)
        manager.add_subordinate(manager)
        manager.add_subordinate(Employee("E1", self.person, "Кассир", 1.0, TODAY))
        self.assertEqual(len(manager.subordinates), 1)
        discount = Discount("Весна", 10, date(2026, 12, 31))
        manager.approve_discount(discount)
        self.assertTrue(discount.is_approved)
        with self.assertRaises(StaffNotQualifiedException):
            manager.approve_discount(Discount("Много", 50, date(2026, 12, 31)))

    def test_manager_refunds_and_complaints(self):
        manager = Manager("M1", self.person, 1500.0, date(2020, 1, 1), approval_limit=100.0)
        payment = PaymentProcessor().charge(make_card(), 500.0, None, TODAY)
        small, big = Refund(payment, 50.0, "a"), Refund(payment, 200.0, "b")
        manager.approve_refund(small)
        self.assertIs(small.approved_by, manager)
        with self.assertRaises(RefundNotAllowedException):
            manager.approve_refund(big)
        client = make_client()
        complaint = Complaint(client, Booking("B1", client, make_package(client=client), TODAY), "Шумно")
        manager.review_complaint(complaint, "Скидка 10%")
        self.assertIs(complaint.status, ComplaintStatus.RESOLVED)

    def test_accountant(self):
        accountant = Accountant("A1", self.person, 1200.0, date(2020, 1, 1))
        client = make_client()
        booking = Booking("B1", client, make_package(client=client), TODAY)
        invoice = accountant.issue_invoice(booking, TODAY)
        self.assertEqual(invoice.calculate_subtotal(), booking.total_price)
        payment = PaymentProcessor().charge(make_card(), 100.0, booking, TODAY)
        refund = Refund(payment, 40.0, "отказ")
        with self.assertRaises(InvalidBookingStateException):
            accountant.process_refund(refund)
        refund.approve(Manager("M1", self.person, 1.0, TODAY))
        accountant.process_refund(refund)
        self.assertIs(refund.status, RefundStatus.EXECUTED)
        report = accountant.generate_sales_report([booking], TODAY, TODAY)
        self.assertEqual(report.calculate_revenue(), 0.0)

    def test_driver(self):
        driver = Driver("D1", self.person, 700.0, date(2020, 1, 1), {"d"})
        city = make_city()
        route = (Address("A", "1", "1", city), Address("B", "2", "2", city))
        transfer = Transfer(route, datetime(2026, 4, 10, 12, 0), Bus("1234", 2, "D", True), 30)
        driver.assign_transfer(transfer)
        self.assertIs(transfer.driver, driver)
        with self.assertRaises(StaffNotQualifiedException):
            driver.assign_transfer(Transfer(route, datetime(2026, 4, 10, 12, 0), Bus("5678", 2, "C", True), 30))


if __name__ == "__main__":
    unittest.main()
