"""Тесты бронирования, оплаты и финансовых документов."""
import unittest
from datetime import date

from tests.factories import (
    CVV,
    START,
    TODAY,
    make_card,
    make_client,
    make_country,
    make_package,
    make_person,
    make_service,
    make_tour,
)
from travel_agency.booking.booking import Booking, Waitlist
from travel_agency.booking.policy import CancellationPolicy
from travel_agency.exceptions import (
    BookingNotFoundException,
    CapacityExceededException,
    CardExpiredException,
    InsufficientFundsException,
    InvalidBookingStateException,
    InvalidPaymentDataException,
    RefundNotAllowedException,
    TourFullyBookedException,
    VisaRequiredException,
)
from travel_agency.finance.cards import BankCard, PaymentProcessor, Refund
from travel_agency.finance.reports import CurrencyConverter, Invoice, SalesReport
from travel_agency.people.staff import Manager
from travel_agency.service.clients import LoyaltyCard
from travel_agency.statuses import BookingStatus, PaymentStatus, RefundStatus


def make_loyal_client():
    client = make_client()
    client.loyalty_card = LoyaltyCard("L1")
    return client


class BookingTest(unittest.TestCase):
    def setUp(self):
        self.client = make_client()
        self.booking = Booking("B1", self.client, make_package(client=self.client, travelers=2), TODAY)

    def test_travelers_and_confirm(self):
        self.booking.add_traveler(make_person())
        with self.assertRaises(CapacityExceededException):
            self.booking.add_traveler(make_person())
        self.booking.confirm()
        self.assertEqual(self.booking.package.tour.booked_places, 2)
        with self.assertRaises(InvalidBookingStateException):
            self.booking.confirm()
        self.booking.complete()
        self.assertIs(self.booking.status, BookingStatus.COMPLETED)
        self.assertFalse(self.booking.is_active())

    def test_cancel_confirmed(self):
        self.booking.calculate_total()
        self.booking.confirm()
        cancellation = self.booking.cancel("болезнь", date(2026, 4, 1))
        self.assertEqual(self.booking.package.tour.booked_places, 0)
        self.assertEqual(cancellation.days_before_departure(), 9)
        self.assertEqual(cancellation.penalty_amount, self.booking.total_price / 2)
        self.assertEqual(cancellation.calculate_refund_amount(self.booking.total_price), self.booking.total_price / 2)
        with self.assertRaises(InvalidBookingStateException):
            self.booking.cancel("ещё раз", TODAY)

    def test_cancel_pending_without_hotel(self):
        self.booking.package.hotel_reservation = None
        self.booking.cancel("передумал", TODAY)
        self.assertIs(self.booking.status, BookingStatus.CANCELLED)
        self.assertEqual(self.booking.destination_name(), "Анталья")


class PolicyAndWaitlistTest(unittest.TestCase):
    def test_policy(self):
        policy = CancellationPolicy()
        self.assertEqual(policy.penalty_percent_for(40), 0)
        self.assertEqual(policy.penalty_percent_for(20), 25)
        self.assertEqual(policy.penalty_percent_for(-1), 100)
        self.assertEqual(policy.calculate_penalty(1000.0, 10), 500.0)

    def test_waitlist(self):
        tour = make_tour(max_group=1)
        waitlist = Waitlist(tour, 2)
        first, second = make_client("C1"), make_client("C2")
        self.assertEqual(waitlist.enqueue(first), 1)
        self.assertEqual(waitlist.enqueue(first), 1)
        self.assertEqual(waitlist.enqueue(second), 2)
        with self.assertRaises(CapacityExceededException):
            waitlist.enqueue(make_client("C3"))
        tour.reserve_places(1)
        self.assertIsNone(waitlist.promote_next())
        tour.release_places(1)
        self.assertIs(waitlist.promote_next(), first)
        self.assertEqual(waitlist.position_of(first), 0)


class BookingServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = make_service()
        self.client = make_loyal_client()
        self.package = make_package(client=self.client)
        self.package.destination_country().add_visa_free_country("BY")

    def test_full_flow(self):
        booking = self.service.create_booking(self.client, self.package, TODAY)
        self.assertEqual(self.service.find_by_client(self.client), [booking])
        payment = self.service.pay_booking(booking.booking_id, self.client.bank_card, TODAY)
        self.assertIs(booking.status, BookingStatus.CONFIRMED)
        self.assertGreater(self.client.loyalty_card.points, 0)
        with self.assertRaises(InvalidBookingStateException):
            self.service.pay_booking(booking.booking_id, self.client.bank_card, TODAY)
        balance_before = self.client.bank_card.balance
        self.service.cancel_booking(booking.booking_id, "болезнь", date(2026, 3, 20))
        self.assertIs(payment.status, PaymentStatus.REFUNDED)
        self.assertEqual(self.client.bank_card.balance, balance_before + payment.amount * 0.75)
        self.assertEqual(len(self.service.notifier.history_for(self.client)), 2)

    def test_errors(self):
        with self.assertRaises(BookingNotFoundException):
            self.service.find_booking("NOPE")
        italy_tour = make_tour(city=None)
        italy_tour.destination.city.country = make_country("Италия", "IT")
        with self.assertRaises(VisaRequiredException):
            self.service.create_booking(self.client, make_package(tour=italy_tour, client=self.client), TODAY)
        self.package.tour.reserve_places(self.package.tour.max_group_size)
        with self.assertRaises(InvalidBookingStateException):
            self.service.create_booking(self.client, self.package, TODAY)

    def test_rollback_when_tour_filled(self):
        booking = self.service.create_booking(self.client, self.package, TODAY)
        self.package.tour.reserve_places(self.package.tour.max_group_size)
        balance = self.client.bank_card.balance
        with self.assertRaises(TourFullyBookedException):
            self.service.pay_booking(booking.booking_id, self.client.bank_card, TODAY)
        self.assertEqual(self.client.bank_card.balance, balance)

    def test_cancel_unpaid_without_loyalty(self):
        self.client.loyalty_card = None
        booking = self.service.create_booking(self.client, self.package, TODAY)
        cancellation = self.service.cancel_booking(booking.booking_id, "x", TODAY)
        self.assertEqual(cancellation.booking, booking)
        self.assertIsNone(self.service._reward_loyalty(self.client, 100.0))


class CardsTest(unittest.TestCase):
    def test_card(self):
        card = make_card(balance=100.0)
        self.assertEqual(card.masked_number, "************1111")
        self.assertTrue(card.verify_cvv(CVV))
        self.assertFalse(card.verify_cvv("999"))
        self.assertEqual(card.withdraw(40.0, TODAY), 60.0)
        self.assertEqual(card.deposit(10.0), 70.0)
        with self.assertRaises(InsufficientFundsException):
            card.withdraw(1000.0, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            card.deposit(0)
        with self.assertRaises(CardExpiredException):
            make_card(expiry=date(2025, 1, 1)).withdraw(1.0, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            BankCard("1234", "X", TODAY, CVV)

    def test_processor(self):
        processor = PaymentProcessor()
        source, target = make_card(balance=1000.0), make_card(balance=0.0)
        self.assertEqual(processor.transfer(source, target, 500.0, TODAY), 5.0)
        self.assertEqual(source.balance, 495.0)
        self.assertEqual(target.balance, 500.0)
        payment = processor.charge(source, 100.0, None, TODAY)
        self.assertEqual(payment.payment_id, "P00002")
        with self.assertRaises(InvalidBookingStateException):
            payment.process()
        processor.rollback(payment)
        self.assertEqual(source.balance, 495.0)
        with self.assertRaises(RefundNotAllowedException):
            payment.refund(1.0)

    def test_payment_refund_validation(self):
        payment = PaymentProcessor().charge(make_card(), 100.0, None, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            payment.refund(200.0)
        payment.refund(0.0)
        self.assertIs(payment.status, PaymentStatus.REFUNDED)

    def test_refund_request(self):
        payment = PaymentProcessor().charge(make_card(), 100.0, None, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            Refund(payment, 500.0, "много")
        refund = Refund(payment, 30.0, "частично")
        with self.assertRaises(RefundNotAllowedException):
            refund.execute()
        refund.reject()
        self.assertIs(refund.status, RefundStatus.REJECTED)
        with self.assertRaises(RefundNotAllowedException):
            refund.approve(Manager("M", make_person(), 1.0, TODAY))


class ReportsTest(unittest.TestCase):
    def setUp(self):
        client = make_client()
        self.booking = Booking("B1", client, make_package(client=client), TODAY)
        self.booking.calculate_total()

    def test_invoice(self):
        invoice = Invoice("I1", self.booking, TODAY)
        invoice.add_item("Тур", 1000.0)
        invoice.add_item("Страховка", 50.0)
        self.assertEqual(invoice.calculate_vat(), 210.0)
        self.assertEqual(invoice.calculate_total(), 1260.0)
        self.assertTrue(invoice.is_overdue(date(2026, 4, 1), False))
        self.assertFalse(invoice.is_overdue(date(2026, 4, 1), True))
        with self.assertRaises(InvalidPaymentDataException):
            invoice.add_item("Ошибка", -1.0)

    def test_converter(self):
        converter = CurrencyConverter()
        converter.update_rate("usd", 1.1, TODAY)
        converter.update_rate("BYN", 3.5, TODAY)
        self.assertEqual(converter.convert(110.0, "USD", "BYN"), 350.0)
        self.assertEqual(converter.last_updated, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            converter.update_rate("XXX", 0, TODAY)
        with self.assertRaises(InvalidPaymentDataException):
            converter.convert(1.0, "XXX", "EUR")

    def test_sales_report(self):
        self.booking.confirm()
        report = SalesReport(TODAY, START, [self.booking])
        self.assertEqual(report.calculate_revenue(), self.booking.total_price)
        self.assertEqual(report.average_check(), self.booking.total_price)
        self.assertEqual(report.top_destinations(), [("Анталья", 1)])
        self.assertEqual(SalesReport(START, START, [self.booking]).average_check(), 0.0)


if __name__ == "__main__":
    unittest.main()
